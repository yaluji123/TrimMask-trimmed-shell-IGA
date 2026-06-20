# Runtime environment

The executable material in this repository is an AutoCAD/ObjectARX plug-in. It
cannot be run as a standalone program on a machine without AutoCAD.

## Tested build target

The bundled binaries in `plugin/AutoCAD_2025_Release_x64/` correspond to a
64-bit AutoCAD/ObjectARX 2025 Release build. The source project used for this
package targets:

- AutoCAD 2025;
- ObjectARX 2025 SDK;
- x64 platform.

ObjectARX binary compatibility is tied to the AutoCAD release. For another
AutoCAD version, the plug-in should normally be rebuilt against the matching
ObjectARX SDK.

## Required software

To load the supplied binaries, a reproduction machine should have:

1. Windows x64;
2. AutoCAD 2025 x64;
3. the files in `plugin/AutoCAD_2025_Release_x64/` kept together in one
   directory;
4. Microsoft Visual C++ runtime components required by the Release build;
5. AutoCAD security settings that allow loading ARX/DBX files from the plug-in
   directory.

Administrator mode is not a mathematical requirement of the plug-in. It may be
useful on machines with strict security policies or protected working
directories, but the usual requirement is that AutoCAD can trust and load the
plug-in directory.

## Is Intel oneAPI required?

Installing the full Intel oneAPI toolkit is not normally required just to run
the packaged plug-in. The plug-in directory includes the MKL/OpenMP runtime
libraries used by this build, including `mkl_core.dll`,
`mkl_intel_thread.dll`, `mkl_avx2.dll`, their `.2.dll` counterparts, and
`libiomp5md.dll`. If these DLLs remain in the same folder as `IGAforCAD.arx`, or
are otherwise visible on the system `PATH`, AutoCAD should be able to resolve
the Intel runtime dependencies without a full oneAPI installation.

oneAPI or the Intel MKL runtime becomes relevant in two cases:

1. the plug-in fails to load because an MKL/OpenMP DLL is missing or
   incompatible;
2. the user wants to rebuild the plug-in from source against Intel MKL.

## Runtime libraries included

The plug-in folder includes the ARX/DBX binaries and dependent numerical runtime
libraries, including BLAS/LAPACK/ARPACK, Intel MKL, OpenMP, and MinGW runtime
DLLs used by the current build. The `.pdb` files are excluded because they are
debug symbols, not execution dependencies, and exceed ordinary repository
file-size limits.

The full `third_party` source/build directory is not required for running the
packaged plug-in. It is only needed when rebuilding the plug-in from source.
For runtime use, keep the ARX, DBX, and bundled DLL files together.

## Loading in AutoCAD

A typical loading sequence is:

1. Start AutoCAD 2025.
2. Add the plug-in directory to AutoCAD trusted paths, or set the security
   policy to allow loading from that directory.
3. Load `IGAforCAD.arx` using AutoCAD's `APPLOAD` command or an equivalent ARX
   loading command.
4. Keep `JYH_IGAEntity.dbx` and the runtime DLLs in the same directory as
   `IGAforCAD.arx`; the ARX module expects to locate the DBX dependency there.

The CSV outputs provided in `data/trim_diagnostics/` are the stable exported
diagnostics for independent inspection.
