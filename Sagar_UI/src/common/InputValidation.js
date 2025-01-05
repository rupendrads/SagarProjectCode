export const positiveNumberOnly = (event) => {
  console.log("keycode", event.keyCode);
  if (
    (event.keyCode === 8 ||
      event.keyCode === 9 ||
      event.keyCode === 190 ||
      (event.keyCode >= 48 && event.keyCode <= 57)) === false
  ) {
    event.preventDefault();
  }
};

export const numberOnly = (event) => {
  if (
    (event.keyCode === 8 ||
      event.keyCode === 9 ||
      event.keyCode === 190 ||
      event.keyCode === 189 ||
      (event.keyCode >= 48 && event.keyCode <= 57)) === false
  ) {
    event.preventDefault();
  }
};
