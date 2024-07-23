(module

  (memory 1)

  (global $__free_mem i32 (i32.const 11)) ;; next available memory region is at dec 11
  (data (i32.const 4) "Ca va?\n")
  (global $__cava__literal_ptr_raw i32 (i32.const 4))

  (func $question (result i32)
    (global.get  $__cava__literal_ptr_raw)
  )
  (export "lib#question" (func $question_0))

)

