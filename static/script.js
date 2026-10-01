// JavaScript do site (antes este arquivo estava vazio, em template/funcionar.js)

// 1) Pede confirmação antes de excluir: qualquer <form data-confirmar="...">
document.querySelectorAll("form[data-confirmar]").forEach(function (form) {
    form.addEventListener("submit", function (evento) {
        if (!confirm(form.dataset.confirmar)) {
            evento.preventDefault(); // cancela o envio
        }
    });
});

// 2) Máscara de telefone: vai formatando (11) 99999-9999 enquanto digita
var campoTelefone = document.getElementById("telefone");
if (campoTelefone) {
    campoTelefone.addEventListener("input", function () {
        var n = campoTelefone.value.replace(/\D/g, "").slice(0, 11);
        if (n.length > 10) {
            n = n.replace(/^(\d{2})(\d{5})(\d{4})$/, "($1) $2-$3");
        } else if (n.length > 6) {
            n = n.replace(/^(\d{2})(\d{4})(\d{0,4})$/, "($1) $2-$3");
        } else if (n.length > 2) {
            n = n.replace(/^(\d{2})(\d*)$/, "($1) $2");
        }
        campoTelefone.value = n;
    });
}

// 3) As mensagens verdes somem sozinhas depois de 4 segundos
document.querySelectorAll(".aviso-ok").forEach(function (aviso) {
    setTimeout(function () {
        aviso.style.opacity = "0";
        setTimeout(function () { aviso.remove(); }, 400);
    }, 4000);
});

// 4) No agendamento, impede escolher uma data que já passou
var campoData = document.getElementById("data_hora");
if (campoData) {
    var agora = new Date();
    agora.setMinutes(agora.getMinutes() - agora.getTimezoneOffset());
    campoData.min = agora.toISOString().slice(0, 16);
}
