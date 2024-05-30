const flatpickr = require("flatpickr");

flatpickr('#datetime', {
  enableTime: true,
  dateFormat: "Y-m-d H:i", 
  defaultDate: "today",
  timezone: "Australia/Sydney"
});