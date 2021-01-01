$(function () {


	function checkBoxShow(triggerElem, targetElem) {
		var trigger = triggerElem
		var target = targetElem

		!trigger.attr("checked") && target.hide()

		trigger && trigger.on('change', function() {
			trigger.is(":checked") ? target.show(600) : target.hide(600);
		})
	}

	checkBoxShow($('#id_direct_sale'), $("label:contains(Add to shop)").parent().parent())
	checkBoxShow($('#id_external_sale'), $("label:contains(Add external sale)").parent().parent())


});
