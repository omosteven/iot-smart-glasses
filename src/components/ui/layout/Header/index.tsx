// import { useAppContext } from "AppContext";
import assets from "assets";
import Button from "components/ui/Button";
import { Link, useNavigate } from "react-router-dom";

const Header = () => {
  const navigate = useNavigate();
  // const { user, token } = useAppContext();

  // const showAdminTab = Boolean(user) && Boolean(token);

  return (
    <header className="layout-header">
      <div className="layout-header__left">
        {/* <img src={assets.images.hero} alt="Forklife" /> */}
        <h3>IoT Smart Glass Dashboard</h3>
        <p>University of Salerno (Steven, Nighat)</p>
      </div>
      {/* {showAdminTab && ( */}
      <div>
        <Button text="Test Device Connectivity" />
      </div>
      {/* )} */}
    </header>
  );
};

export default Header;
