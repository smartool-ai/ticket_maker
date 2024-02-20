import logo from "../static/logo.svg";
import logoInverted from "../static/logo_inverted.svg";

export default function Logo({ inverted, size = "lg" }) {
  const logoSizes = {
    sm: "h-12 w-12 z-10",
    md: "h-20 w-20 z-10",
    lg: "h-28 w-28 z-10",
  };

  const logoBackgroundSizes = {
    sm: "h-6 w-6",
    md: "h-10 w-10",
    lg: "h-16 w-16",
    default: "bg-white absolute z-1",
  };

  const combineClassNames = (id, classNameObject) => [classNameObject[id], classNameObject.default].join(" ");

  return (
    <div className="relative flex items-center justify-center">
      <div className={combineClassNames(size, logoBackgroundSizes)}></div>
      <img
        className={logoSizes[size]}
        src={inverted ? logoInverted : logo}
        alt="Transcriber"
      />
    </div>
  )
}
