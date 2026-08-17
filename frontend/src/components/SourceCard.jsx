function SourceCard({ sources }) {

    const uniqueSources = [];
    const seen = new Set();

    sources.forEach((source) => {

        const title = source.title;

        if (!title || seen.has(title)) {
            return;
        }

        seen.add(title);
        uniqueSources.push(title);

    });

    return (
        <div className="source-card">

            <div className="source-header">
                <span className="source-line"></span>
                <span>Sources</span>
            </div>

            <div className="source-list">

                {uniqueSources.map((title, index) => (

                    <div
                        className="source-item"
                        key={index}
                    >
                        <span className="source-dot"></span>
                        <span>{title}</span>
                    </div>

                ))}

            </div>

        </div>
    );
}

export default SourceCard;