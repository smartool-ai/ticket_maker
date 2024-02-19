import logo from "../static/logo.svg";
import logoInverted from "../static/logo_inverted.svg";

export default function Logo({ inverted, size = "lg" }) {
  const sizes = {
    "sm": "h-12 w-12",
    "md": "h-20 w-20",
    "lg": "h-28 w-28",
  }

  return <img
    className={sizes[size]}
    src={inverted ? logoInverted : logo}
    alt="Transcriber"
  />
}
