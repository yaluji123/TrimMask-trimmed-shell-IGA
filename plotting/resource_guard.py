"""Self-owned CPU1/512MiB guard. It never changes another process."""
import ctypes
from ctypes import wintypes
import os

LIMIT = 512 * 1024**2
_job_handle = None


def install():
    global _job_handle
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[key] = "1"
    result = {"memory_limit_bytes": LIMIT, "BLAS_threads_requested": 1,
              "OS_memory_job_installed": False, "CPU_affinity_cores": None}
    if os.name != "nt":
        raise RuntimeError("This bounded diagnostic launcher is Windows-specific")
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.GetProcessAffinityMask.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p]
    kernel.SetProcessAffinityMask.argtypes = [wintypes.HANDLE, ctypes.c_size_t]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    process = kernel.GetCurrentProcess()
    process_mask, system_mask = ctypes.c_size_t(), ctypes.c_size_t()
    if not kernel.GetProcessAffinityMask(process, ctypes.byref(process_mask),
                                         ctypes.byref(system_mask)):
        raise ctypes.WinError(ctypes.get_last_error())
    selected = process_mask.value & -process_mask.value
    if not selected or not kernel.SetProcessAffinityMask(process, ctypes.c_size_t(selected)):
        raise ctypes.WinError(ctypes.get_last_error())
    result.update(CPU_affinity_cores=1, CPU_affinity_mask=selected)

    class Basic(ctypes.Structure):
        _fields_ = [("process_time", ctypes.c_int64), ("job_time", ctypes.c_int64),
                    ("flags", wintypes.DWORD), ("minimum_ws", ctypes.c_size_t),
                    ("maximum_ws", ctypes.c_size_t), ("active_processes", wintypes.DWORD),
                    ("affinity", ctypes.c_size_t), ("priority", wintypes.DWORD),
                    ("scheduling", wintypes.DWORD)]

    class IO(ctypes.Structure):
        _fields_ = [(name, ctypes.c_uint64) for name in
                    ("read_ops", "write_ops", "other_ops", "read_bytes", "write_bytes", "other_bytes")]

    class Extended(ctypes.Structure):
        _fields_ = [("basic", Basic), ("io", IO), ("process_memory", ctypes.c_size_t),
                    ("job_memory", ctypes.c_size_t), ("peak_process", ctypes.c_size_t),
                    ("peak_job", ctypes.c_size_t)]

    kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel.CreateJobObjectW.restype = wintypes.HANDLE
    kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int,
                                             ctypes.c_void_p, wintypes.DWORD]
    kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    job = kernel.CreateJobObjectW(None, None)
    if job:
        info = Extended()
        info.basic.flags = 0x100  # JOB_OBJECT_LIMIT_PROCESS_MEMORY
        info.process_memory = LIMIT
        if (kernel.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info))
                and kernel.AssignProcessToJobObject(job, process)):
            _job_handle = job
            result["OS_memory_job_installed"] = True
        else:
            result["job_error"] = ctypes.get_last_error()
            kernel.CloseHandle(job)
    else:
        result["job_error"] = ctypes.get_last_error()
    return result


def actual_budget(n, input_nnz):
    if n != 729 or not 0 < input_nnz <= 200000:
        raise ValueError("Only the actual bounded 729-DOF input is admitted")
    # Includes a full worst-case sparse LU, dense input/pencils and interpreter reserve.
    breakdown = {"interpreter_and_libraries_reserve": 160 * 1024**2,
                 "captured_dense_K_and_coefficient_work": 6 * n * n * 8,
                 "worst_full_sparse_LU_and_work": 8 * n * n * 16,
                 "local_pencil_work": 16 * 243 * 243 * 8,
                 "input_and_derived_sparse_matrices": 16 * input_nnz * 24,
                 "basis_trace_and_vector_reserve": 16 * 1024**2}
    total = sum(breakdown.values())
    if total >= LIMIT:
        raise MemoryError("Explicit actual sparse budget exceeds 512 MiB")
    return {"major_and_runtime_reserve_bytes": total, "breakdown": breakdown,
            "limit_bytes": LIMIT, "dimension": n, "actual_input_nnz": input_nnz}
