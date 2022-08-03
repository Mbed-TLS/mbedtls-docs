# Arm Thumb error: r7 cannot be used in asm here

## Platform

Arm (Thumb assembly).

## What

Depending on the GCC compiler options used, you can receive an error:

    error: r7 cannot be used in asm here
    
## Reason

The assembly code in `bn_mul.h` is optimized for the Arm platform and uses some registers, including `r7` to efficiently perform an operation. GCC also uses `r7` as the frame pointer under the Arm Thumb assembly.

## Solution

Add `-fomit-frame-pointer` to your GCC compiler options.

If you have already added for example `-O` or `-O2` you do not need to add `-fomit-frame-pointer` as the optimization options already include it on most systems by default.
