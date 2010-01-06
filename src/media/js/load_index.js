jQuery.loadIndex = function(element, callback) {
    element.load('/include', function(){
        callback();
    });
};

