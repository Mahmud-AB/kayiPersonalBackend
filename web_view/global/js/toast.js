(function ($) {
    showSuccessToast = function (msg) {
        'use strict';
        resetToastPosition();
        $.toast({
            heading: 'Success',
            text: msg,
            showHideTransition: 'slide',
            icon: 'success',
            loaderBg: '#f96868',
            position: 'top-right'
        })
    };
    showInfoToast = function (msg) {
        'use strict';
        resetToastPosition();
        $.toast({
            heading: 'Info',
            text: msg,
            showHideTransition: 'slide',
            icon: 'info',
            loaderBg: '#46c35f',
            position: 'top-right'
        })
    };
    showWarningToast = function (msg) {
        'use strict';
        resetToastPosition();
        $.toast({
            heading: 'Warning',
            text: msg,
            showHideTransition: 'slide',
            icon: 'warning',
            hideAfter: 5000,
            loaderBg: '#57c7d4',
            position: 'top-right'
        })
    };
    showDangerToast = function (msg) {
        'use strict';
        resetToastPosition();
        $.toast({
            heading: 'Error',
            text: msg,
            showHideTransition: 'slide',
            icon: 'error',
            hideAfter: 5000,
            loaderBg: '#f2a654',
            position: 'top-right'
        })
    };
    showToastPosition = function (position, msg) {
        'use strict';
        resetToastPosition();
        $.toast({
            heading: 'Positioning',
            text: msg,
            position: String(position),
            icon: 'info',
            stack: false,
            loaderBg: '#f96868'
        })
    }
    showToastInCustomPosition = function (msg) {
        'use strict';
        resetToastPosition();
        $.toast({
            heading: 'Custom positioning',
            text: msg,
            icon: 'info',
            position: {
                left: 120,
                top: 120
            },
            stack: false,
            loaderBg: '#f96868'
        })
    }
    resetToastPosition = function () {
        $('.jq-toast-wrap').removeClass('bottom-left bottom-right top-left top-right mid-center'); // to remove previous position class
        $(".jq-toast-wrap").css({
            "top": "",
            "left": "",
            "bottom": "",
            "right": ""
        });
    }
})(jQuery);

(function ($) {
    showSwal = function (type) {
        'use strict';
        if (type === 'basic') {
            swal({
                text: 'Any fool can use a computer',
                button: {
                    text: "OK",
                    value: true,
                    visible: true,
                    className: "btn btn-primary"
                }
            })

        } else if (type === 'title-and-text') {
            swal({
                title: 'Read the alert!',
                text: 'Click OK to close this alert',
                button: {
                    text: "OK",
                    value: true,
                    visible: true,
                    className: "btn btn-primary"
                }
            })

        } else if (type === 'success-message') {
            swal({
                title: 'Congratulations!',
                text: 'You entered the correct answer',
                icon: 'success',
                button: {
                    text: "Continue",
                    value: true,
                    visible: true,
                    className: "btn btn-primary"
                }
            })

        } else if (type === 'auto-close') {
            swal({
                title: 'Auto close alert!',
                text: 'I will close in 2 seconds.',
                timer: 2000,
                button: false
            }).then(
                function () {
                },
                // handling the promise rejection
                function (dismiss) {
                    if (dismiss === 'timer') {
                        console.log('I was closed by the timer')
                    }
                }
            )
        } else if (type === 'warning-message-and-cancel') {
            swal({
                title: 'Are you sure?',
                text: "You won't be able to revert this!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3f51b5',
                cancelButtonColor: '#ff4081',
                confirmButtonText: 'Great ',
                buttons: {
                    cancel: {
                        text: "Cancel",
                        value: null,
                        visible: true,
                        className: "btn btn-danger",
                        closeModal: true,
                    },
                    confirm: {
                        text: "OK",
                        value: true,
                        visible: true,
                        className: "btn btn-primary",
                        closeModal: true
                    }
                }
            })

        } else if (type === 'custom-html') {
            swal({
                content: {
                    element: "input",
                    attributes: {
                        placeholder: "Type your password",
                        type: "password",
                        class: 'form-control'
                    },
                },
                button: {
                    text: "OK",
                    value: true,
                    visible: true,
                    className: "btn btn-primary"
                }
            })
        }
    }

})(jQuery);