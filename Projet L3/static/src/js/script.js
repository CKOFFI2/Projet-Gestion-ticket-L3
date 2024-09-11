odoo.define('event_qr_code.frontend', function (require) {

    var rpc = require('web.rpc')

    const html5QrCode = new Html5Qrcode('reading')
    const config = { fps: 10, qrbox: { width: 250, height: 250 } }

    $('#ScanModal').on('hidden.bs.modal', function (e) {
        html5QrCode.stop()
    });

    $('#scanResult').on('hidden.bs.modal', function (e) {
        $('#resultText').text('')
        $('#scanResult #resultIcon i').remove()
    });

    function scanSuccess(decodedText, decodedResult) {
        var json_result = JSON.parse(decodedText)
        console.log('json_result', json_result)
        var code = json_result.code
        html5QrCode.stop()

        if (code) {
            var data = {
                'code': code,
                'event_id': $('#eventId').val(),
            }
            console.log('data...', data)
            rpc.query({
                model: 'event.registration',
                method: 'check_registration',
                args: [data],
            })
                .then(function (response) {
                    console.log('response...', response)
                    $('#ScanModal').modal("hide")
                    var icon, result
                    if (response) {
                        if (response == 'draft') {
                            icon = 'window-close text-muted'
                            result = 'Non confirmé'
                        }
                        else if (response == 'cancel') {
                            icon = 'window-close text-danger'
                            result = 'Annulé'
                        }
                        else if (response == 'open') {
                            icon = 'check-circle text-success'
                            result = 'Confirmé'
                        }
                        else if (response == 'done') {
                            icon = 'window-close text-danger'
                            result = 'Déjà scanné'
                        }
                        else {
                            icon = 'window-close text-danger'
                            result = 'Non trouvé'
                        }
                    } else {
                        icon = 'window-close text-danger'
                        result = 'Non trouvé'
                    }
                    $('#resultText').text(result)
                    $('#scanResult #resultIcon').append(`<i class="fas fa-${icon}" style="font-size: 10em;"/>`)
                    $('#scanResult').modal("show")
                })
                .catch((error) => {
                    console.log("Error...", error);
                });

        }
        else {
            console.log('Invalid code...', code)
        }
    }

    function doc_ready(fn) {
        if (
            document.readyState === 'complete' ||
            document.readyState === 'interactive'
        ) {
            setTimeout(fn, 1)
        } else {
            document.addEventListener('DOMContentLoaded', fn)
        }
    }

    $("#scan_turnstile").on('click', function () {
        doc_ready(function () {
            html5QrCode.start(
                { facingMode: 'environment' },
                config,
                scanSuccess
            )
            $('#scan_stop').on('click', function () {
                html5QrCode.stop()
            })
        })

    });

});