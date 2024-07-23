(module
  (memory 1)
  (memory 1)
  (export "memory" (memory 0))
  (export "memory" (memory 0))

  (func $main)
  (export "example:host/lib#schedule" (func $main))

  (import "example:host/lib" "schedule" (func $totally_not_main))

  (func $other
    (call $totally_not_main)
  )
)
