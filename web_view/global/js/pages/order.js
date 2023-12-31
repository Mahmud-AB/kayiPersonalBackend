$(document).ready(function () {

});

function cancelHoleOrder(orderId) {
    swal({
        title: 'Alert!',
        text: "Do you want to perform this action?",
        type: 'info',
        confirmButtonText: 'Cancel'
    }).then((okayClick) => {
        if (okayClick === true || okayClick.value === true) {
            window.swal({title: "Processing...", text: "Please wait", imageUrl: "https://d157777v0iph40.cloudfront.net/unified3.0/images/ajax-loader-blue.gif", showConfirmButton: false, allowOutsideClick: false});
            $.ajax({
                url: "/api/product/order/order-cancel-by-shop/" + orderId,
                data: new FormData(),
                cache: false, contentType: false, processData: false, method: 'POST', type: 'POST',
                success: function (data) {
                    if (data.status) {
                        window.swal({title: "Cancel successfully", showConfirmButton: false, allowOutsideClick: false});
                        setTimeout(new function () {
                            window.location.href = window.location.href
                        }, 1500)
                    } else {
                        showDangerToast(data.message)
                        swal.close()
                    }
                },
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                    showDangerToast("Failed! Something went wrong")
                    swal.close()
                }
            });
        }
    });
}

function cancelHoleOrderIndivisual(orderId, itemId) {
    swal({
        title: 'Alert!',
        text: "Do you want to perform this action?",
        type: 'info',
        confirmButtonText: 'Cancel'
    }).then((okayClick) => {
        if (okayClick === true || okayClick.value === true) {
            window.swal({title: "Processing...", text: "Please wait", imageUrl: "https://d157777v0iph40.cloudfront.net/unified3.0/images/ajax-loader-blue.gif", showConfirmButton: false, allowOutsideClick: false});
            $.ajax({
                url: "/api/product/order/order-cancel-by-shop/" + orderId + "?item=" + itemId,
                data: new FormData(),
                cache: false, contentType: false, processData: false, method: 'POST', type: 'POST',
                success: function (data) {
                    if (data.status) {
                        window.swal({title: "Cancel successfully", showConfirmButton: false, allowOutsideClick: false});
                        setTimeout(new function () {
                            window.location.href = window.location.href
                        }, 1500)
                    } else {
                        showDangerToast(data.message)
                        swal.close()
                    }
                },
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                    showDangerToast("Failed! Something went wrong")
                    swal.close()
                }
            });
        }
    });
}

function processingHoleOrder(orderId) {
    swal({
        title: 'Alert!',
        text: "Do you want to perform this action?",
        type: 'info',
        confirmButtonText: 'Processing'
    }).then((okayClick) => {
        if (okayClick === true || okayClick.value === true) {
            window.swal({title: "Processing...", text: "Please wait", imageUrl: "https://d157777v0iph40.cloudfront.net/unified3.0/images/ajax-loader-blue.gif", showConfirmButton: false, allowOutsideClick: false});
            $.ajax({
                url: "/api/product/order/change-status/" + orderId + "?status=PROCESSING",
                data: new FormData(),
                cache: false, contentType: false, processData: false, method: 'POST', type: 'POST',
                success: function (data) {
                    if (data.status) {
                        window.swal({title: "Added successfully", showConfirmButton: false, allowOutsideClick: false});
                        setTimeout(new function () {
                            window.location.href = window.location.href
                        }, 1500)
                    } else {
                        showDangerToast(data.message)
                        swal.close()
                    }
                },
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                    showDangerToast("Failed! Something went wrong")
                    swal.close()
                }
            });
        }
    });
}

function transitHoleOrder(orderId) {
    swal({
        title: 'Alert!',
        text: "Do you want to perform this action?",
        type: 'info',
        confirmButtonText: 'Transit'
    }).then((okayClick) => {
        if (okayClick === true || okayClick.value === true) {
            window.swal({title: "Processing...", text: "Please wait", imageUrl: "https://d157777v0iph40.cloudfront.net/unified3.0/images/ajax-loader-blue.gif", showConfirmButton: false, allowOutsideClick: false});
            $.ajax({
                url: "/api/product/order/change-status/" + orderId + "?status=TRANSIT",
                data: new FormData(),
                cache: false, contentType: false, processData: false, method: 'POST', type: 'POST',
                success: function (data) {
                    if (data.status) {
                        window.swal({title: "Added successfully", showConfirmButton: false, allowOutsideClick: false});
                        setTimeout(new function () {
                            window.location.href = window.location.href;
                        }, 1500);
                    } else {
                        showDangerToast(data.message);
                        swal.close();
                    }
                },
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                    showDangerToast("Failed! Something went wrong");
                    swal.close();
                }
            });
        }
    });
}

function shippingHoleOrder(orderId) {
    swal({
        title: 'Alert!',
        text: "Do you want to perform this action?",
        type: 'info',
        confirmButtonText: 'Shipping'
    }).then((okayClick) => {
        if (okayClick === true || okayClick.value === true) {
            window.swal({title: "Processing...", text: "Please wait", imageUrl: "https://d157777v0iph40.cloudfront.net/unified3.0/images/ajax-loader-blue.gif", showConfirmButton: false, allowOutsideClick: false});
            $.ajax({
                url: "/api/product/order/change-status/" + orderId + "?status=SHIPPING",
                data: new FormData(),
                cache: false, contentType: false, processData: false, method: 'POST', type: 'POST',
                success: function (data) {
                    if (data.status) {
                        window.swal({title: "Added successfully", showConfirmButton: false, allowOutsideClick: false});
                        setTimeout(new function () {
                            window.location.href = window.location.href
                        }, 1500)
                    } else {
                        showDangerToast(data.message)
                        swal.close()
                    }
                },
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                    showDangerToast("Failed! Something went wrong")
                    swal.close()
                }
            });
        }
    });
}

function completeOrder(orderId) {
    swal({
        title: 'Alert!',
        text: "Do you want to perform this action?",
        type: 'info',
        confirmButtonText: 'Complete'
    }).then((okayClick) => {
        if (okayClick === true || okayClick.value === true) {
            window.swal({title: "Processing...", text: "Please wait", imageUrl: "https://d157777v0iph40.cloudfront.net/unified3.0/images/ajax-loader-blue.gif", showConfirmButton: false, allowOutsideClick: false});
            $.ajax({
                url: "/api/product/order/change-status/" + orderId + "?status=COMPLETE",
                data: new FormData(),
                cache: false, contentType: false, processData: false, method: 'POST', type: 'POST',
                success: function (data) {
                    if (data.status) {
                        window.swal({title: "Added successfully", showConfirmButton: false, allowOutsideClick: false});
                        setTimeout(new function () {
                            window.location.href = window.location.href
                        }, 1500)
                    } else {
                        showDangerToast(data.message)
                        swal.close()
                    }
                },
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                    showDangerToast("Failed! Something went wrong")
                    swal.close()
                }
            });
        }
    });
}