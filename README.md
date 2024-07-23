# WatCat

## What?

This is not a cat. A picture of a cat is included at the end. This is poor man's linker or bundler for WAT.

## Okey, really

If your want to bundle two web assemble text files together that reference one another two imports
you have two options:

- don't work with .wat files and do something more real, like using wasm as a target of llvm or rust;
- use wasi component model which requires defining interfaces and doesn't support circular dependencies
  and doesn't want you to export tags or memory.


This small pack of glue and duct take full of bugs is providing the thing option


## Example


Imagine you have two files like this:


```
;; main.wat

(module

  (memory 1)

  (global $__free_mem i32 (i32.const 17)) ;; next available memory region is at dec 17
  (data (i32.const 4) "Hello world!\n")
  (global $__hello__literal_ptr_raw i32 (i32.const 4))

  (import "lib" "question" (func $question (result i32)))

  (func $main
    (call $question) (drop)
  )
  (export "main#main" (func $main))
)

;; lib.wat

(module

  (memory 1)

  (global $__free_mem i32 (i32.const 11)) ;; next available memory region is at dec 11
  (data (i32.const 4) "Ca va?\n")
  (global $__cava__literal_ptr_raw i32 (i32.const 4))

  (func $question (result i32)
    (global.get  $__cava__literal_ptr_raw)
  )
  (export "lib#question" (func $question))

)

```


Now you can combine them with `watmerge.py out.wat main.wat lib.wat`, which will do the following:

- combine data segments into one linear memory, i.e. data segment 4 of the second file moves to 21 (dec);
- adjust global constants that hold memory pointers to data segments with prefixed offsets (i.e. `$__cava__literal_ptr_raw` will point to 21 dec as it should);
- point `$__free_mem` to the next available offset of combined memory;
- prefix variable names in both files with `module_main_fn__` and `module_lib_fn__` respectibely;
- replace imports with variables, i.e. `(call $question)` becomes `(call $module_lib_question_fn__question)`.


Normally this is something that linker should do, but I haven't found any for my use case.

## Want to contribute?

If you want to fix some bugs, typos or rewrite the whole thing in erlang or webassembler, send me a PR with a picture of cat.


## A cat

Here is an image of the cat.

![The crime scete](https://github.com/muromec/watcat/blob/main/cat.jpg?raw=true)
