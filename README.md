
## protocol

    
    Client                  Server
           join->
                 <-room_init
           key_press->
               <-room_update 
           key_press->
               <-room_update


#### room_init

    tiles: [
        {
            type: 'wall'
            coords: (x, y)
            stats: {is_visible: True}
        },{
            type: 'wall'
            coords: (x, y)
            stats: {is_visible: True}
        },{
            type: 'floor'
            coords: (x, y)
            stats: {is_visible: True}
        }
    players: [
        {
            name: ''
            coords: (x, y)
            stats...
        }
    ]
    creatures: []


#### room_update
    tiles: [
        # new tiles
    ]
    players: [
         # updated players
    ]


