$(document).ready(function () {
    $('.p-zipcode').select2();
    $('.js-example-basic-single').select2();

    const image_crop = $('#image_crop_view').croppie({enableExif: true, viewport: {width: 300, height: 300, type: 'square'}, boundary: {width: 400, height: 400}});
    $('#browse-category-image').on('change', function () {
        //TODO $('#browse-category-image-popup').modal('show');
        const reader = new FileReader();
        /*TODO reader.onload = function (event) {
            image_crop.croppie('bind', {
                url: event.target.result
            }).then(function () {
                console.log('jQuery bind complete');
            });
        }*/
        reader.onloadend = function () {
            $('#browse-category-image-show').attr('src', reader.result);
        };
        reader.readAsDataURL(this.files[0]);
    });
    $('#crop-save').click(function () {
        image_crop.croppie('result', {type: 'canvas', size: 'viewport'}).then(function (response) {
            $('#browse-category-image-show').attr('src', response);
        })
        $('#browse-category-image-popup').modal('hide');
    });

    $('#save-category-now').click(function () {
        const dataSet = {
            "parent": $("#categoryParent").val(),
            "name": $("#categoryName").val(),
            "zipcode": getALlSelectedZipCodes('.p-zipcode'),
            "image": $("#browse-category-image-show").attr("src"),
            "deliveryUs": $("input:radio[name='delivery_flag']").prop("checked")
        };
        saveCategoryNow(dataSet);
    });

    $('#update-category-now').click(function () {
        const dataSet = {
            "id": globalCategoryId,
            "parent": $("#categoryParent").val(),
            "name": $("#categoryName").val(),
            "zipcode": getALlSelectedZipCodes('.p-zipcode'),
            "image": $("#browse-category-image-show").attr("src"),
            "delivery_flag": $("input:radio[name='delivery_flag']").prop("checked")
        };
        saveCategoryNow(dataSet);
    });

    $('#cancel-category-now').click(function () {
        globalCategoryId = ""
        $('.p-zipcode').val([]).trigger('change');
        $("#categoryName").val("")
        $("#categoryParent").val('').trigger('change');
        $('#save-category-now').css('display', 'inline-block');
        $('#update-category-now').css('display', 'none');
        $('#cancel-category-now').css('display', 'none');
        $('#add-update-category').text('Add New Category/Subcategory');
        $("#browse-category-image-show").attr("src", "/public/img/browse-file.gif")
    });

    $('.edit-category-option').click(function () {
        let data = $(this).attr("val")
        data = JSON.parse(data)

        window.scrollTo(0, 0);
        $('#save-category-now').css('display', 'none');
        $('#update-category-now').css('display', 'inline-block');
        $('#cancel-category-now').css('display', 'inline-block');
        $('#add-update-category').text('Update category');
        $("#delivery_flag1").prop("checked", data['delivery_flag']);
        $("#delivery_flag2").prop("checked", data['delivery_flag'] == true ? false : true);

        $('.p-zipcode').val(data.cities).trigger('change');
        $('#browse-category-image-show').attr('src', data.image);
        $("#categoryName").val(data.name)
        if (data.parent != null) {
            $("#categoryParent").val(data.parent).trigger('change');
        } else {
            $("#categoryParent").val('').trigger('change');
        }
        globalCategoryId = data.id
        console.log(data)
    });

    $('.delete-category-option').click(function () {
        let id = $(this).attr("val");
        swal({
            title: 'Alert!',
            text: "Do you want to perform this action",
            type: 'error',
            confirmButtonText: 'Delete'
        }).then((okayClick) => {
            if (okayClick === true || okayClick.value == true) {
                showSuccessToast("Category deleting")
                $.get("/api/product/categories-delete?id=" + id, function (data, status) {
                    if (status == 'success') {
                        if (data.status) {
                            showSuccessToast(data.message)
                            setInterval(function () {
                                window.location.href = ''
                            }, 1000)
                        } else {
                            showDangerToast(data.message)
                        }
                    } else {
                        showDangerToast("Something went wrong")
                    }
                });
            }
        });
    });

    $('.select2-container').css('width', '100%')
});

let globalCategoryId = "";

function saveCategoryNow(jsonData) {
    swal({text: "Please wait! Processing...", button: false})
    $.post("/api/product/categories-save", jsonData, function (data, status) {
        if (status == 'success') {
            if (data.status) {
                showSuccessToast(data.message)
                setInterval(function () {
                    window.location.reload()
                }, 1000)
            } else {
                swal({title: "Error", text: data.message})
            }
        } else {
            swal({title: "Error", text: "Something went wrong"})
        }
    });
}

function getALlSelectedZipCodes(id) {
    var selectedZipCodes = []
    for (let x = 0; x < $(id).val().length; x++) {
        if ($(id).val()[x] == "0") {
            selectedZipCodes = [0]
            break;
        } else {
            for (let y = 0; y < allZipCodes.length; y++) {
                if ($(id).val()[x] == allZipCodes[y].city) {
                    for (let z = 0; z < allZipCodes[y].zipcodes.length; z++) {
                        selectedZipCodes.push(allZipCodes[y].zipcodes[z]);
                    }
                }
            }
        }
    }
    return selectedZipCodes.toString();
}