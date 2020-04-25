
## setup

    virtualenv env
    env/bin/activate
    pip install -r requirements.txt


## trying out map generators

    python main.py gen-map GENRATORNAME
    python main.py gen-map dummy


## protocol

    
    Client                  Server
           join->
                 <-init
           key_press->
               <-update 
           key_press->
               <-update
               
               # player disconnect
               

#### init
    
    type: init
    data: 
        self: 
            coords: (0, 0)
            color: 254
        map:
          - - (0, 0)
            - 'wall'
            - true, true  # seen, is_visible
          - - (3, 1)
            - 'floor'
            - true, false  # seen, is_visible
          ...
        players:
            uid123: 
                coords: (0, 0)
                color: 254
            uid234: 
                coords: (0, 0)
                color: 254
        creatures:
            uid345:
                type: blob
                coords: (0, 0)
                is_visible: true,
                color: 254

#### update

same as init, but only changes
    
    type: update
    data: ...


#### remove_players

since update just sends the updates, and a non-existing player would not be part od the update, we need to remove them explicitly

    type: remove_players
    data: 
        - uid1
        - uid2
           ...

#### remove_creatures

    type: remove_creatures
    data:
        - uid42
