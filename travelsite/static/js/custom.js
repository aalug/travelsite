(function ($) {

    "use strict";

    $('.owl-show-events').owlCarousel({
        items: 4,
        loop: true,
        dots: true,
        nav: true,
        autoplay: true,
        margin: 30,
        responsive: {
            0: {
                items: 1
            },
            600: {
                items: 2
            },
            1000: {
                items: 4
            }
        }
    })

    const second = 1000,
        minute = second * 60,
        hour = minute * 60,
        day = hour * 24;

    let countDown = new Date('Mar 31, 2022 09:30:00').getTime(),
        x = setInterval(function () {

            let now = new Date().getTime(),
                distance = countDown - now;

            document.getElementById('days').innerText = Math.floor(distance / (day)),
                document.getElementById('hours').innerText = Math.floor((distance % (day)) / (hour)),
                document.getElementById('minutes').innerText = Math.floor((distance % (hour)) / (minute)),
                document.getElementById('seconds').innerText = Math.floor((distance % (minute)) / second);

            //do something later when date is reached
            //if (distance < 0) {
            //  clearInterval(x);
            //  'IT'S MY BIRTHDAY!;
            //}

        }, second)

    $(function () {
        $("#tabs").tabs();
    });


    $('.schedule-filter li').on('click', function () {
        var tsfilter = $(this).data('tsfilter');
        $('.schedule-filter li').removeClass('active');
        $(this).addClass('active');
        if (tsfilter == 'all') {
            $('.schedule-table').removeClass('filtering');
            $('.ts-item').removeClass('show');
        } else {
            $('.schedule-table').addClass('filtering');
        }
        $('.ts-item').each(function () {
            $(this).removeClass('show');
            if ($(this).data('tsmeta') == tsfilter) {
                $(this).addClass('show');
            }
        });
    });


    // Window Resize Mobile Menu Fix
    mobileNav();


    // Scroll animation init
    window.sr = new scrollReveal();


    // Menu Dropdown Toggle
    if ($('.menu-trigger').length) {
        $(".menu-trigger").on('click', function () {
            $(this).toggleClass('active');
            $('.header-area .nav').slideToggle(200);
        });
    }


    // Page loading animation
    $(window).on('load', function () {

        $('#js-preloader').addClass('loaded');

    });


    // Window Resize Mobile Menu Fix
    $(window).on('resize', function () {
        mobileNav();
    });


    // Window Resize Mobile Menu Fix
    function mobileNav() {
        var width = $(window).width();
        $('.submenu').on('click', function () {
            if (width < 767) {
                $('.submenu ul').removeClass('active');
                $(this).find('ul').toggleClass('active');
            }
        });
    }

})(window.jQuery);


// place the cart item quantity on load
$('.item_qty').each(function () {
    let the_id = $(this).attr('id')
    let qty = $(this).attr('data-qty')
    $('#' + the_id).html(qty)
})

// decrease cart
$('.decrease_cart').on('click', function (e) {
    e.preventDefault();

    food_id = $(this).attr('data-id');
    url = $(this).attr('data-url');
    cart_id = $(this).attr('id');


    $.ajax({
        type: 'GET',
        url: url,
        success: function (response) {
            console.log(response)
            if (response.status == 'login_required') {
                swal(response.message, '', 'info').then(function () {
                    window.location = '/login';
                })
            } else if (response.status == 'Failed') {
                swal(response.message, '', 'error')
            } else {
                $('#cart_counter').html(response.cart_counter['cart_count']);
                $('#qty-' + food_id).html(response.qty);

                applyCartAmounts(
                    response.cart_amount['subtotal'],
                    response.cart_amount['tax_dict'],
                    response.cart_amount['grand_total']
                )

                if (window.location.pathname == '/cart/') {
                    removeCartItem(response.qty, cart_id);
                    checkEmptyCart();
                }

            }
        }
    })
})


// DELETE CART ITEM
$('.delete_cart').on('click', function (e) {
    e.preventDefault();

    cart_id = $(this).attr('data-id');
    url = $(this).attr('data-url');


    $.ajax({
        type: 'GET',
        url: url,
        success: function (response) {
            console.log(response)
            if (response.status == 'Failed') {
                swal(response.message, '', 'error')
            } else {
                $('#cart_counter').html(response.cart_counter['cart_count']);
                swal(response.status, response.message, "success")

                applyCartAmounts(
                    response.cart_amount['subtotal'],
                    response.cart_amount['tax_dict'],
                    response.cart_amount['grand_total']
                )

                removeCartItem(0, cart_id);
                checkEmptyCart();
            }
        }
    })
})


// delete the cart element if the qty is 0
function removeCartItem(cartItemQty, cart_id) {
    if (cartItemQty <= 0) {
        // remove the cart item element
        document.getElementById("cart-item-" + cart_id).remove()
    }

}

// Check if the cart is empty
function checkEmptyCart() {
    let cart_counter = document.getElementById('cart_counter').innerHTML
    if (cart_counter == 0) {
        document.getElementById("empty-cart").style.display = "block";
    }
}

// apply cart amounts
function applyCartAmounts(subtotal, tax_dict, grand_total) {
    if (window.location.pathname == '/cart/') {
        $('#subtotal').html(subtotal)
        $('#total').html(grand_total)

        console.log(tax_dict)
        for (key1 in tax_dict) {
            console.log(tax_dict[key1])
            for (key2 in tax_dict[key1]) {
                // console.log(tax_dict[key1][key2])
                $('#tax-' + key1).html(tax_dict[key1][key2])
            }
        }
    }
}
