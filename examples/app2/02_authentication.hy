(setv initialization
      (Flow
        :name "initialization"
        :request (Request
                   :method "POST"
                   :path "/auth/login.php"
                   :data {"open" "login"})
        :outputs [csrf_name csrf_value session_id]
        :operations [(Http
                       :status 200
                       :action (NextStage "login"))]))


(setv login
      (Flow
        :name "login"
        :request (Request
                   :method "POST"
                   :path "/auth/login.php"
                   :cookies [session_id]
                   :data
                   {"open" "login"
                    "action" "customerlogin"
                    "password" password
                    "username" username
                    "redirect" "myaccount"
                    csrf_name csrf_value})
        :outputs [csrf_name csrf_value]
        :operations [(Http
                       :status 200
                       :action (NextStage "multi_factor")
                       :otherwise (NextStage "login"))]))


(setv multi_factor
      (Flow
        :name "multi_factor"
        :request (Request
                   :method "POST"
                   :path "/auth/login.php"
                   :cookies [session_id]
                   :data
                     {"open" "login"
                      "action" "customerlogin"
                      "redirect" "myaccount"
                      "twofactorcode" mfa_code
                      csrf_name csrf_value})
        :outputs [init_vector verify]
        :operations [(Http
                       :status 200
                       :action (NextStage None))
                     (Http
                       :status 403
                       :action (NextStage "initialization"))]))




(setv _authentication
      [initialization
       login
       multi_factor])
