import { Loader } from "components/ui";
import { useEffect } from "react";

const Detections = ({
  detections,
}: {
  detections: { texts: string; detections: any[]; time_taken?: any }[];
}) => {
  useEffect(() => {
    if (document) {
      document.getElementById("bottom")?.scrollIntoView();
    }
  }, [detections]);
  return (
    <section className="main__detections">
      <h5>Reading Real-time Detections</h5>
      <div className="main__detections__container">
        {detections.map(({ texts, detections, time_taken }, index) => (
          <section className="main__detections__each" key={index}>
            <b>
              Detection No : {index + 1} - Took: {time_taken?.toFixed?.(2)} secs
            </b>
            <p>Texts: {texts || "Non Found"}</p>
            <p>
              Objects:{" "}
              {detections.length > 0 ? (
                <>
                  {detections.map(({ object }, pos) => (
                    <span key={pos}>{object}</span>
                  ))}
                </>
              ) : (
                "Non Found"
              )}
            </p>
          </section>
        ))}
        <div id="bottom"></div>

        {/* <Loader
          loaderType="CIRCULAR"
          loaderText="Checking for detection logs"
        /> */}
      </div>
    </section>
  );
};

export default Detections;
