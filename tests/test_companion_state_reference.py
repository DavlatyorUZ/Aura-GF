"""All eight authored poses retain the supplied state-reference character."""
from pathlib import Path
from PIL import Image
import numpy as np
import pytest
from desktop_app.companion_painter import CompanionPose,render_companion

pytestmark=pytest.mark.unit
STATES=('asleep','idle','listening','thinking','launching','speaking','dictating','dictation_processing')
CENTRES=(153,386,618,850,1081,1313,1546,1778)

@pytest.mark.parametrize('state,centre',list(zip(STATES,CENTRES)))
def test_each_activity_matches_its_reference_pose(state,centre):
    original=Image.open(Path(__file__).parent/'fixtures/face/state-reference.png').convert('RGB')
    padded=Image.new('RGB',(max(original.width,max(CENTRES)+117),original.height),(247,248,251))
    padded.paste(original,(0,0))
    source=padded.crop((centre-117,476,centre+117,744))
    frame=render_companion(CompanionPose(state=state))
    assert (frame.width(),frame.height()) == source.size
    frame=frame.convertToFormat(frame.Format.Format_RGBA8888)
    actual=Image.frombytes('RGBA',source.size,frame.constBits().asstring(frame.sizeInBytes()))
    background=Image.new('RGB',source.size,(247,248,251));background.paste(actual,mask=actual.getchannel('A'))
    difference=np.abs(np.array(source).astype(float)-np.array(background).astype(float))
    assert difference.mean()<7
    assert np.mean(difference.max(axis=2)>40)<.055


@pytest.mark.parametrize('state',STATES)
def test_reference_canvas_has_no_opaque_padding_at_its_edges(state):
    frame=render_companion(CompanionPose(state=state))
    assert all(frame.pixelColor(frame.width()-1,y).alpha()==0 for y in range(frame.height()))
    assert all(frame.pixelColor(x,0).alpha()==0 for x in range(frame.width()))
    assert all(frame.pixelColor(x,frame.height()-1).alpha()==0 for x in range(frame.width()))
