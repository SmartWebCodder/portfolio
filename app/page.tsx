import DevsyncPage from "@/components/devsync/DevsyncPage";
import Sprite from "@/components/devsync/Sprite";
import Reveal from "@/components/Reveal";
import Accordion from "@/components/Accordion";
import ImageFade from "@/components/ImageFade";

export default function Page() {
  return (
    <>
      <Sprite />
      <DevsyncPage />
      <Reveal />
      <Accordion />
      <ImageFade />
    </>
  );
}
