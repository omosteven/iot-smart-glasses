export const getAuthToken = () => {
  let token = localStorage.getItem("userToken");
  return token;
};

export const setAuthToken = (token: string) => {
  localStorage.setItem("userToken", token);
};
