(setv nickname
      (Html
        :name "nickname"
        :tag "input"
        :attributes
        {:type "text"
         :name "name"}
        :extract "value"))

(setv get_nickname
      (Flow
        :name "get_nickname"
        :request (Request
                   :method "GET"
                   :cookies [session_id init_vector verify]
                   :path "/my-details")
        :outputs [nickname]
        :operations [(Print nickname)]))

(setv _functions [get_nickname])
