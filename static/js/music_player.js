var player_flag = false;
var myin2
function play_pause(id, btn_id, c_id, time){
    btn = document.getElementById(btn_id)
    sound = document.getElementById(id)
    counter = document.getElementById(c_id)
    sound. addEventListener('ended',
        function() {
            this. currentTime = 0;
            player_flag = false;
            btn.innerHTML = "<img src='/static/icons/play-fill.svg' width='20px' height='20px' class='file-icon'>";
            clearInterval(myin1)
            myin2 = setInterval(function () {
                counter.innerHTML = time
            }, 1000)
        }, false);




    if (player_flag == false){
        sound.play();
        btn.innerHTML = "<img src='/static/icons/pause.svg' width='20px' height='20px' class='file-icon'>";
        clearInterval(myin2)
        myin1 = setInterval(function () {
            // if (player_flag == false) {

            var s1 = parseInt(sound.duration % 60);
            var m1 = parseInt((sound.duration / 60) % 60);

            var s = parseInt(sound.currentTime % 60);
            var m = parseInt((sound.currentTime / 60) % 60);
            counter.innerHTML = m + ':' + s + " " + m1 + ':' + s1;

            // if (player_flag == true){
            //             counter.innerHTML = time
            //
            // }

            // }}, 1000)
        }, 1000)
        player_flag = true;
    }
    else if (player_flag == true){
        btn.innerHTML = "<img src='/static/icons/play-fill.svg' width='20px' height='20px' class='file-icon'>";
        counter.innerHTML = time
        sound.pause();
        clearInterval(myin1)
        // myin2 = setInterval(function () {
            counter.innerHTML = time
        // }, 1000)
        player_flag = false;
    }
}

// var played = sound.played;
//
// setTimeout(function(){
//     counter.style = "width:" + played + "px;"
//
// }, 1000)