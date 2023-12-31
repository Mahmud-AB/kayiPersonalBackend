$(document).ready(function () {
    $('.product-seller-but').click(function () {
        let uId = $(this).attr("val");
        window.location.href="/service/product/list/"+uId;
    });
    $('.active-seller-but').click(function () {
        let uId = $(this).attr("val");
        swal({
            title: 'Alert!',
            text: "Do you want to perform this action?",
            type: 'info',
            confirmButtonText: 'Active'
        }).then((okayClick) => {
            if (okayClick === true || okayClick.value == true) {
                showInfoToast("Please wait");
                $.post("/api/user/active", {'id': uId}).done(
                    function (data) {
                        if (data.status) {
                            showSuccessToast(data.message)
                            setInterval(function () {
                                window.location.reload()
                            }, 1000)
                        } else {
                            showDangerToast(data.message)
                        }
                    }
                ).fail(
                    function (jqXHR, textStatus, errorThrown) {
                        showDangerToast("Something went wrong")
                    }
                );
            }
        });
    });

    $('.remove-seller-but').click(function () {
        let uId = $(this).attr("val");
        swal({
            title: 'Alert!',
            text: "Do you want to perform this action?",
            type: 'error',
            confirmButtonText: 'Delete'
        }).then((okayClick) => {
            if (okayClick === true || okayClick.value == true) {
                showInfoToast("Please wait");
                $.post("/api/user/remove", {'id': uId}).done(
                    function (data) {
                        if (data.status) {
                            showSuccessToast(data.message)
                            setInterval(function () {
                                window.location.reload()
                            }, 1000)
                        } else {
                            showDangerToast(data.message)
                        }
                    }
                ).fail(
                    function (jqXHR, textStatus, errorThrown) {
                        showDangerToast("Something went wrong")
                    }
                );
            }
        });
    });
    $('.deactivate-seller-but').click(function () {
        let uId = $(this).attr("val");
        swal({
            title: 'Alert!',
            text: "Are you want to deactivate?",
            type: 'error',
            confirmButtonText: 'Deactivate'
        }).then((okayClick) => {
            if (okayClick === true || okayClick.value == true) {
                showInfoToast("Please wait");
                $.post("/api/user/deactivate", {'id': uId}).done(
                    function (data) {
                        if (data.status) {
                            showSuccessToast(data.message)
                            setInterval(function () {
                                window.location.reload()
                            }, 1000)
                        } else {
                            showDangerToast(data.message)
                        }
                    }
                ).fail(
                    function (jqXHR, textStatus, errorThrown) {
                        showDangerToast("Something went wrong")
                    }
                );
            }
        });
    });
});