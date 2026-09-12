/**
 * The Devsync page shell: the template's own wrapper elements, with each
 * section rendered by its own component so the DOM nesting is unchanged.
 */
import HeroSpacer from "./HeroSpacer";
import Hero from "./Hero";
import About from "./About";
import Works from "./Works";
import Service from "./Service";
import Process from "./Process";
import Client from "./Client";
import Blog from "./Blog";
import Nav from "./Nav";
import Footer from "./Footer";
import LiftedScope from "../lifted/LiftedScope";
import FastfolioSprite from "../lifted/Sprite";
import SkillsSection from "../lifted/SkillsSection";
import ExperienceSection from "../lifted/ExperienceSection";
import TestimonialsSection from "../lifted/TestimonialsSection";

export default function DevsyncPage() {
  return (
    <div className="framer-R2Reu framer-mw7bu8" data-framer-cursor="qpjp1d" data-layout-template="true" style={{minHeight: "100vh", width: "auto"} as React.CSSProperties}>
    <Nav />
    <style data-framer-html-style="">{"html body { background: var(--token-bb0c0bd9-9918-415b-81a2-622ee217b736, rgb(17, 17, 17)); }"}</style>
    <div data-framer-root="" className="framer-jyVT1 framer-KCs8o framer-G3fkC framer-azZvx framer-ZWCWD framer-y9fN6 framer-eh8Mo framer-8SSIa framer-72rtr7" style={{minHeight: "100vh", width: "auto", display: "contents"} as React.CSSProperties}>
    <main className="framer-1ga29be" data-framer-name="Main">
    <FastfolioSprite />
    <HeroSpacer />
    <Hero />
    <About />
    <LiftedScope><SkillsSection /></LiftedScope>
    <Works />
    <Service />
    <LiftedScope><ExperienceSection /></LiftedScope>
    <Process />
    <LiftedScope><TestimonialsSection /></LiftedScope>
    <Client />
    <Blog />
    </main>
    </div>
    <div id="overlay"></div>
    <div className="framer-ik1xi8"></div>
    <Footer />
    </div>
  );
}
