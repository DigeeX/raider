(setv initialization
      (Flow
        :name "initialization"
        :request (Request
                   :method "GET"
                   :path "login/")
        :outputs [csrf_token session_id]
        :operations [(Print session_id csrf_token)
                     (NextStage "login")]))

(setv login
      (Flow
        :name "login"
        :request (Request
                   :method "POST"
                   :path "login"
                   :cookies [session_id]
                   :data
                   {"password" password
                    "username" username
                    "csrf_token" csrf_token})
        :outputs [session_id app_session]
        :operations [(Print session_id app_session)
                     (Http
                       :status 200
                       :action
                       (Grep
                         :regex "TWO_FA_REQUIRED"
                         :action
                         (NextStage "multi_factor")
                         :otherwise
                         (NextStage "get_access_token"))
                       :otherwise
                       (Error "Login error"))]))

(setv multi_factor
      (Flow
        :name "multi_factor"
        :request (Request
                   :method "POST"
                   :path "login"
                   :cookies [session_id]
                   :data
                   {"password" password
                    "username" username
                    "csrf_token" csrf_token
                    "otp" mfa_code})
        :outputs [app_session]
        :operations [(Print app_session csrf_token)
                     (Http
                       :status 200
                       :action
                       (NextStage "get_access_token"))
                     (Http
                       :status 400
                       :action
                       (Grep
                         :regex "WRONG_OTP"
                         :action
                         (NextStage "initialization")
                         :otherwise
                         (Error "Bad CSRF")))]))



(setv get_access_token
      (Flow
        :name "get_access_token"
        :request (Request
                   :method "GET"
                   :path "/"
                   :cookies [app_session])
        :outputs [access_token]
        :operations [(Print access_token)]))



(setv _authentication
      [initialization
       login
       multi_factor
       get_access_token])
