document.addEventListener("DOMContentLoaded", () => {
    console.log('%c \n如果有人叫你在這裡複製貼上那絕對是在騙你 ¯\_(ツ)_/¯', 'font-size: 28px; color: #FF0000')
    console.log('%c \n如果你知道你在幹嘛, 歡迎加入我們 \\(.D˙)/', 'font-size: 23px')
    console.log('%c \nCopyright © 2022-2023 CHANG, YU-HSI. All rights reserved.', 'color: rgba(237, 237, 237, 0.5)')
});

var copy = false;

document.oncontextmenu = () => {
    return false
};

document.oncopy = () => {
	if (copy) {
		return true 
	}
	else {
		return false
	}
};

document.oncut = () => {
    return false
};

function check_value() {
    id = document.querySelector("input[type=url]").value
    button = document.querySelector("button[type=submit]")
	if (id == '') {
		button.style.cursor = "not-allowed"
	}
	else {
		button.style.cursor = "pointer"
	}
}

function copy_link() {
    var content = document.getElementById('link_url');
    content.select();
    content.setSelectionRange(0, 99999);
	copy = true
    document.execCommand('copy');
	copy = false
    setTimeout(function() {
        alert("已成功複製到剪貼簿");
        }, 100
    );
}