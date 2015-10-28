jQuery(document).ready(function($) {
  $(".datepicker-widget").datepicker({
                                       maxDate: 0,
                                       dateFormat: "dd/mm/yy",
                                       showOn: "both",
                                       buttonImage: "++theme++gites.theme/images/icon_calendrier.png",
                                       buttonImageOnly: true,
                                       changeMonth: true,
                                       changeYear: true,
                                       defaultDate: -10950,
                                       stepMonths: 12
                                     });
});
