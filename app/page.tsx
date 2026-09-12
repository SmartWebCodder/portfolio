import DevsyncPage from "@/components/devsync/DevsyncPage";
import Sprite from "@/components/devsync/Sprite";
import Loader from "@/components/Loader";
import Reveal from "@/components/Reveal";
import Accordion from "@/components/Accordion";
import Services from "@/components/Services";
import Counters from "@/components/Counters";
import Menu from "@/components/Menu";
import ImageFade from "@/components/ImageFade";

export default function Page() {
  return (
    <>
      <Loader />
      <Sprite />
      <DevsyncPage />
      <Reveal />
      <Accordion />
      <Services />
      <Counters />
      <Menu />
      <ImageFade />
    </>
  );
}
