(module

  (memory 1)

  (global $__free_mem i32 (i32.const 17)) ;; next available memory region is at dec 17
  (data (i32.const 4) "Hello world!\n")
  (global $__hello__literal_ptr_raw i32 (i32.const 4))

  (import "lib" "question" (func $question (result i32)))

  (func $main
    (call $question) (drop)
  )
)

