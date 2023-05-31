
document.addEventListener("DOMContentLoaded", function() {
    var title = document.title
    title = title.toLowerCase();
    
    
    switch(title){
        case "dashboard":
            var element = document.getElementById("1");
            break;
        case "spending":
            var element = document.getElementById("2");
            break;
        case "goals":
            var element = document.getElementById("3");
            break;
        case "notifications":
            var element = document.getElementById("4");
            break;
        case "settings":
            var element = document.getElementById("5");
            break;
        case "user":
            var element = document.getElementById("6");
            break;
        case "logout":
            var element = document.getElementById("7");
            break;
        default:
            var element = document.getElementById("6");
            break;  
    }
    element.classList.add('chosen');
});