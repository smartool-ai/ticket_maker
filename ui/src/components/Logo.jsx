import logo from "../static/logo.svg";
import logoInverted from "../static/logo_inverted.svg";

export default function Logo({ className, inverted }) {
  return <img
    className={className}
    src={inverted ? logoInverted : logo}
    alt="Transcriber"
    style={{ height: "100px", width: "100px"}}
  />
}
