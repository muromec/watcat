
(module  
    (memory      1 
    )  
    (export      memory       
        (memory          0 
        )
    )  
    (func      $module_testmod_0_main 
    )  
    (export      example:host/lib#schedule       
        (func          $module_testmod_0_main 
        )
    )  
    (func      $module_testmod_0_other       
        (call          $module_testmod_0_main 
        )
    )
)