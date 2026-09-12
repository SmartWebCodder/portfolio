import DevsyncPage from "@/components/devsync/DevsyncPage";
import Sprite from "@/components/devsync/Sprite";
import Reveal from "@/components/Reveal";
import Accordion from "@/components/Accordion";

export default function Page() {
  return (
    <>
      <Sprite />
      <DevsyncPage />
      <Reveal />
      <Accordion />
    </>
  );
}
