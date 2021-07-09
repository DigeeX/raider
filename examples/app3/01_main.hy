(print "App3")
(setv _base_url "https://app3.org")

(setv username (Variable "username"))
(setv password (Variable "password"))
(setv mfa_code (Prompt "MFA"))

(setv csrf_token
      (Html
        :name "csrf_token"
        :tag "meta"
        :attributes
        {:content "^[A-Za-z0-9+/=]+$"
	 :name "csrf-token"}
        :extract "content"))

(setv session_id (Cookie "session_id"))
(setv remember_user (Cookie "remember_user_token"))
