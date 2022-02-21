import useBaseUrl from "@docusaurus/useBaseUrl";
import React from "react";
import clsx from "clsx";
import styles from "./HomepageFeatures.module.css";

type FeatureItem = {
  title: string;
  image: string;
  description: JSX.Element;
};

const FeatureList: FeatureItem[] = [
  {
    title: "Easy to Use",
    image: "/img/undraw_docusaurus_mountain.svg",
    description: (
      <>
        Rath was designed from the ground up to be easily installed and used
        with your favorite technologies.
      </>
    ),
  },
  {
    title: "Composable",
    image: "/img/undraw_docusaurus_tree.svg",
    description: (
      <>
        Include complex logic in your api calls, but keep your code simple and
        reusable.
      </>
    ),
  },
  {
    title: "Powered by Async",
    image: "/img/undraw_docusaurus_react.svg",
    description: (
      <>
        Rath was designed async first but provides convenience for sync methods
      </>
    ),
  },
];

function Feature({ title, image, description }: FeatureItem) {
  return (
    <div className={clsx("col col--4")}>
      <div className="text--center padding-horiz--md padding-top--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): JSX.Element {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
