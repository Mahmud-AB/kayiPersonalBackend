let simpleMDEObj;
$(document).ready(function () {
    var selectedImage = "0";
    for (var xxxx = 1; xxxx <= 4; xxxx++) {
        $('#browseImg' + xxxx).on('change', function () {
            selectedImage = this.id.replace("browseImg", "");
            const reader = new FileReader();
            reader.onloadend = function () {
                uploadProductImage(reader.result, selectedImage);
            };
            reader.readAsDataURL(this.files[0]);
        });
    }
    simpleMDEObj = new SimpleMDE({
        element: document.getElementById('p_description'),
        initialValue: $('#temp_value_1').html(),
        hideIcons: ['guide', 'fullscreen', 'side-by-side']
    });
});

function uploadProductImage(response, selectedImage) {
    window.swal({title: "Processing...", text: "Please wait", imageUrl: "https://d157777v0iph40.cloudfront.net/unified3.0/images/ajax-loader-blue.gif", showConfirmButton: false, allowOutsideClick: false});
    $.ajax({
        url: "/api/product/save/image",
        type: "POST",
        data: {"image": response, "image_index": selectedImage, "product_id": $('#product_id').val()},
        success: function (data) {
            swal.close();
            $('#uploadimageModal').hide();
            if (data.status) {
                const productId = $('#product_id').val();
                $("#im-column-00" + selectedImage).html('' +
                    '<div class="delete-product-image" onclick="deleteProductImg(' + productId + ',' + selectedImage + ')">' +
                    '    <i class="mdi mdi-delete text-large text-white"></i>' +
                    '</div>' +
                    '<div class="im-card">' +
                    '    <label class="cursor-pointer">' +
                    '        <img for="browseImg' + selectedImage + '" id="browseImgShow' + selectedImage + '" src="' + response + '" width="100%"/>' +
                    '        <input type="file" visbility="hidden" style="display: none;" id="browseImg' + selectedImage + '">' +
                    '    </label>' +
                    '</div>' +
                    '');
                showSuccessToast("Uploaded successfully");
            } else {
                data.message.forEach(function (ms) {
                    console.log(ms);
                    showDangerToast(ms);
                })
            }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            swal.close();
            showDangerToast("Something went wrong");
            $('#uploadimageModal').hide();
        }
    });
}

function saveProduct() {
    const productId = $("#product_id").val();
    let price1 = $("#p_price").val().trim() === '' ? '0' : $("#p_price").val().trim();
    let price2 = $("#p_price_new").val().trim() === '' ? '0' : $("#p_price_new").val().trim();
    if (price1 === "0") {
        if (price2 !== "0") {
            price1 = price2;
        }
    }
    if (price2 === "0") {
        if (price1 !== "0") {
            price2 = price1;
        }
    }

    var dataSet = new FormData();
    dataSet.append("name", $("#p_name").val());
    dataSet.append("category", $("#p_category1").val());
    dataSet.append("price", price1);
    dataSet.append("price_new", price2);
    dataSet.append("weight", JSON.stringify({type: $("#p_size_type").val(), value: $("#p_size").val()}));
    dataSet.append("available", $("#p_stock").val());
    dataSet.append("display", $("#p_display").is(":checked") ? false : true);
    dataSet.append("descriptions", simpleMDEObj.value());
    dataSet.append("descriptions_html", simpleMDEObj.markdown(simpleMDEObj.value()));
    window.swal({title: "Processing...", text: "Please wait", imageUrl: "https://d157777v0iph40.cloudfront.net/unified3.0/images/ajax-loader-blue.gif", showConfirmButton: false, allowOutsideClick: false});
    $.ajax({
        url: "/api/product/save/" + $("#product_id").val(),
        data: dataSet,
        cache: false,
        contentType: false,
        processData: false,
        method: 'POST',
        type: 'POST',
        success: function (data) {
            if (data.status) {
                if (productId === "0") {
                    window.swal({title: "Add successfully", showConfirmButton: false, allowOutsideClick: false});
                } else {
                    window.swal({title: "Update successfully", showConfirmButton: false, allowOutsideClick: false});
                }
                setTimeout(new function () {
                    window.location.href = "../add/" + data.data;
                }, 1500);

            } else {
                data.message.forEach(function (ms) {
                    showDangerToast(ms);
                });
                swal.close();
            }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            showDangerToast("Failed! Something went wrong");
            swal.close();
        }
    });
}

function deleteProductImg(productId, imgSequence) {
    window.swal({title: "Deleting...", text: "Please wait", imageUrl: "https://d157777v0iph40.cloudfront.net/unified3.0/images/ajax-loader-blue.gif", showConfirmButton: false, allowOutsideClick: false});
    $.ajax({
        url: "/api/product/img/delete/" + productId + "/" + imgSequence,
        type: "POST",
        data: {},
        success: function (data) {
            swal.close();
            if (data.status) {
                $("#im-column-00" + imgSequence).html('' +
                    '<label class="cursor-pointer">' +
                    '    <img for="browseImg' + imgSequence + '" id="browseImgShow' + imgSequence + '" src="/public/img/browse-file.gif"/>' +
                    '    <input type="file" visbility="hidden" style="display: none;" id="browseImg' + imgSequence + '">' +
                    '</label>')
                showSuccessToast("Product image deleted successfully");
                window.location.href = "../add/" + productId;
            } else {
                data.message.forEach(function (ms) {
                    showDangerToast(ms);
                })
            }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            swal.close();
            showDangerToast("Something went wrong");
        }
    });
}