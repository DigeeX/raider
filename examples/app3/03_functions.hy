(setv nickname
      (Html
        :name "nickname"
        :tag "input"
        :attributes
        {:id "display_name"}
        :extract "data"))

(setv get_nickname
      (Flow
        :name "get_nickname"
        :request (Request
                   :method "GET"
                   :cookies [session_id remember_user]
                   :path "/settings/profile")
        :outputs [nickname]
        :operations [(Print nickname)]))


(setv _functions [get_nickname])
