import { icons } from "./icons";
import "./Icon.scss";

const Icon = (props: {
  icon: string;
  color?: string;
  className?: string;
  src?: string;
  onClick?: Function;
}) => {
  const { icon, color, className, src, onClick } = props;
  return (
    <>
      {src ? (
        <div className="custom-icon" onClick={() => onClick?.()}>
          <img
            src={src}
            className={`custom-icon__img || ${className}`}
            alt={"Icon"}
          />
        </div>
      ) : (
        <i
          className={`${icons[icon as keyof typeof icons]} || ${className}`}
          aria-hidden="true"
          style={{ color }}
          onClick={() => onClick?.()}
        />
      )}
    </>
  );
};

export default Icon;
