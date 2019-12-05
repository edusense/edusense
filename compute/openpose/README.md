EduSense Openpose
=================

## Developer Guide

### Keeping up with OpenPose Releases

When compiling, we inject our EduSense code into OpenPose code base. OpenPose is
a library under active development; our code often fails to compile because of
code changes (e.g., API and data structure) in newer versions of OpenPose. We need
to update our code whenever we integrate newer OpenPose into EduSense.

We release our EduSense code as patch diff files. The original source code we derive
the current patch files from is /openpose/examples/tutorial_api_cpp/16_synchronous_custom_output.cpp .
The file names of the code changes time to time, so we need to track file changes
across OpenPose versions.

To generate a diff patch file,

```
diff <original file> <new edusense file> > edusense/edusense.cpp.patch
```

Once the patch file is ready, we also need to modify Dockerfile to update the path
to the original source file. A new patch file lacks license notices, so
we need to update the patch file also.

To apply a patch to a file:

```
patch <original file> -i examples/edusense/edusense.cpp.patch -o examples/edusense/edusense.cpp
```

If a developer also wants to update CMakefile, he/she can follow the same instructions
noted above.
