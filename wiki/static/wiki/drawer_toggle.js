function move_left_bar() {
    let checkbox = document.getElementById("checkbox");
    let transform_block = document.getElementById("menu");
    let background = document.getElementById("menu-background");
    if (checkbox.checked) {
        transform_block.style.transform = "translate(0, 0)";
        background.style.opacity = "0.6";
    } else {
        transform_block.style.transform = "translate(-100%, 0)";
        background.style.opacity = "0";
    }
}