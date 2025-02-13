export const helper = () => {};

export const getErrorMessage = (error: any) => {
  const response = error?.response;
  const defaultMssg = "Something went wrong. Please try again.";
  const has500xError = response?.status?.toString?.()?.includes?.("50");
  const errorMessage = has500xError
    ? defaultMssg
    : response?.data
    ? response?.data?.detail || response?.data?.message
    : defaultMssg;

  return errorMessage;
};

export const getFormattedDate = (date?: string) => {
  let monthList = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sept",
    "Oct",
    "Nov",
    "Dec",
  ];

  let dateTime = date ? new Date(date) : new Date();

  let fullYear = dateTime.getFullYear();
  let month = dateTime.getMonth();
  let day = dateTime.getDate();
  let dayString = String(day);
  if (day < 10 && day > 0) {
    dayString = `0${day}`;
  }

  let hour = dateTime.getHours();
  let minute = dateTime.getMinutes();

  return `${dayString} ${monthList[month]} ${fullYear} ${hour}:${minute}`;
};

//const emailRegex = /\S+@\S+\.\S+/;
// const validateEmail = (event: { target: { value: any } }) => {
//   const email = event.target.value;
//   if (emailRegex.test(email)) {
//     setIsValid(true);
//     setMessage("You Just Entered a Valid Email!");
//   } else {
//     setIsValid(false);
//     setMessage("Please Enter a Valid Email!");
//   }
// }

export const scrollChatToBottom = (ref: any) => {
  try {
    ref?.current.scrollIntoView({ behavior: "smooth" });
  } catch (e) {}
};

export const copyToClipboard = async (text: any) => {
  await navigator.clipboard.writeText(text);
};
