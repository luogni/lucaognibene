ts_from_db_to_ay = (t, addsec=0) ->
    ts = Date.parse t
    ts.add
        seconds: addsec
    ts.toString "yyyyMMddHHmmss"

display_one = (d) ->
    tsall = (ts_from_db_to_ay d.eventts, sec for sec in [-2, 0, 2])
    url = ("http://192.168.1.50/ayapi?args=%5B%22admin%22%2C%22c8e3bef8a9f70725bbc6045a8f7aed4e%22%2C#{d.camera}%2C%22#{ts}%22%2C%22image%5C%2Fjpeg%2Cwidth%3D90%22%2Cfalse%5D&method=ay_archive_get_frame_as_image" for ts in tsall)
    imgs = ("<img src=\"#{u}\">" for u in url).join("")
    "<li class=\"\">#{imgs}<p>#{d.eventts}</p></li>"


$.ajax 'http://192.168.1.50/ayapi?args=%5B%22admin%22%2C%22c8e3bef8a9f70725bbc6045a8f7aed4e%22%2C%5B%22event%22%5D%2C%22%22%2C%22%22%2C%5B%22eventts%22%5D%2C%22desc%22%2C0%2C10%2C%22%28%24evtype+%3D%3D+%5C%22MOTION%5C%22%29%22%2C%22%22%2C%22%22%2C%5B%22id%22%2C%22eventts%22%2C%22camera%22%5D%5D&method=ay_object_list',
    type: 'GET'
    dataType: 'json'
    error: (jqXHR, textStatus, errorThrown) ->
        $('body').append "AJAX Error: #{textStatus}"
    success: (data, textStatus, jqXHR) ->
        console.log "rpc ok", data.success
        $('#wookcontainer').append display_one d for d in data.data
        $('#wookcontainer').wookmark
            align: 'center'
            autoResize: true
            direction: 'left'
            itemWidth: 100
        $('#wookcontainer').imagesLoaded()
            .always(->
                console.log "loaded all"
                $('#wookcontainer').trigger 'refreshWookmark'
        )
            

        
