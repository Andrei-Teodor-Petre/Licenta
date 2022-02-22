import {Card, Elevation, Classes} from "@blueprintjs/core/dist/core.bundle";
import './list.css';

function List(){
    return(
        <Card className={Classes.PRIMARY, Classes.DARK} interactive={true} elevation={Elevation.TWO}>
            <h5>We did it!</h5>
            <p>managed to succesfully implement the frontend stack as a trial!</p>
            <div className="List">
                <ul>
                    <li>List item 1</li>
                    <li>List item 2</li>
                </ul>
            </div>
        </Card>

    );
}


  
export default List;