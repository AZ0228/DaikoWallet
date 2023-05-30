var object = document.getElementById('rectangle');

document.addEventListener('mousemove', moveObject);

function moveObject(event) {
var objectRect = object.getBoundingClientRect();
var objectCenterX = objectRect.left + objectRect.width / 2;
var objectCenterY = objectRect.top + objectRect.height / 2;

var mouseX = event.clientX;
var mouseY = event.clientY;

var distanceX = mouseX - objectCenterX;
var distanceY = mouseY - objectCenterY;

var moveX = distanceX * 0.01; //adjust the movement speed as desired
var moveY = distanceY * 0.01;

object.style.transform = 'translate(' + moveX + 'px, ' + moveY + 'px)';
}

var object1 = document.getElementById('gradient');
var object2 = document.getElementById('hero-text');

document.addEventListener('mousemove', moveObject1);

function moveObject1(event) {
var objectRect = object.getBoundingClientRect();
var objectCenterX = objectRect.left + objectRect.width / 2;
var objectCenterY = objectRect.top + objectRect.height / 2;

var mouseX = event.clientX;
var mouseY = event.clientY;

var distanceX = mouseX - objectCenterX;
var distanceY = mouseY - objectCenterY;

var moveX = -(distanceX * 0.01); //adjust the movement speed as desired
var moveY = -(distanceY * 0.01);

object1.style.transform = 'translate(' + moveX + 'px, ' + moveY + 'px)';
//object2.style.transform = 'translate(' + moveX + 'px, ' + moveY + 'px)';

}