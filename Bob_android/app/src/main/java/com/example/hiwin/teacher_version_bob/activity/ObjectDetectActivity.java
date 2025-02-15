package com.example.hiwin.teacher_version_bob.activity;

import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.os.*;
import android.speech.tts.TextToSpeech;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import com.example.hiwin.teacher_version_bob.communication.bluetooth.framework.SerialListener;
import com.example.hiwin.teacher_version_bob.utils.DataSpeaker;
import com.example.hiwin.teacher_version_bob.data.Face;
import com.example.hiwin.teacher_version_bob.fragment.*;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

import static com.example.hiwin.teacher_version_bob.Constants.getObjectDrawableId;

public class ObjectDetectActivity extends DetectActivity {
    private static final String THIS_LOG_TAG = "ObjectDetectActivity";
    private Context context;
    private DataSpeaker speaker;


    @Override
    protected String getDeviceAddress(Bundle savedInstanceState) {
        Intent it = getIntent();
        return it.getStringExtra("address");
    }


    @Override
    protected void initialize(Bundle savedInstanceState) {
        super.initialize(savedInstanceState);

        context = this;
        speaker = new DataSpeaker(new TextToSpeech(context, status -> {
            if (status != TextToSpeech.ERROR) {

                Log.d(THIS_LOG_TAG, "TextToSpeech is initialized");
                Toast.makeText(context, "TextToSpeech is initialized", Toast.LENGTH_SHORT).show();
            } else {
                Log.d(THIS_LOG_TAG, "TextToSpeech initializing error");
                Toast.makeText(context, "TextToSpeech initializing error", Toast.LENGTH_SHORT).show();
            }
        }));
    }

    private void onComplete() {
        showDefault();
    }

    private void showFace(Face face, String name, String tr_name, String sentence, String tr_sentence) throws IOException {
        Fragment finalFaceFragment = getFinalFaceFragment(face, null, "null");
        Fragment exampleFragment = getExampleFragment(sentence, tr_sentence, finalFaceFragment, "face2");
        Fragment faceFragment = getFaceFragment(face, name, tr_name, sentence, tr_sentence, exampleFragment, "example");
        Fragment descriptionFragment = getDescriptionFragment(name, tr_name, faceFragment, "face");
        postFragment(descriptionFragment, "description");
    }

    @Override
    protected void receive(byte[] data) {
        try {
            String content = new String(data, StandardCharsets.UTF_8);
            Log.d(THIS_LOG_TAG, "received string:");
            Log.d(THIS_LOG_TAG, content);

            try {
                detect_pause();
                JSONObject object = new JSONObject(content);

//                builder.setId(json.getInt("id"));
//                builder.setResponseType(json.getString("response_type"));
//                builder.setContent(json.getString("content"));

                JSONObject jdata = object.getJSONObject("data");

                JSONArray languages = jdata.getJSONArray("languages");

                JSONObject translated = null;
                for (int i = 0; i < languages.length(); i++) {
                    if (languages.getJSONObject(i).get("code").equals("zh_TW"))
                        translated = languages.getJSONObject(i);
                }

                if (translated == null)
                    throw new RuntimeException("code not found");

                Face face = Face.valueOf(jdata.getString("face"));
                String name = jdata.getString("name");
                String sentence = jdata.getString("sentence");
                String tr_name = translated.getString("tr_name");
                String tr_sentence = translated.getString("tr_sentence");

                showFace(face, name, tr_name, sentence, tr_sentence);
            } catch (Exception e) {
                Log.e(THIS_LOG_TAG, e.getMessage());
            }
        } catch (IllegalArgumentException e) {
            Log.d(THIS_LOG_TAG, e.getMessage());
        }

    }

    @Override
    protected void showDefault() {
        final DefaultFragment fragment = new DefaultFragment();
        fragment.setListener(new FragmentListener() {
            @Override
            public void start() {
            }

            @Override
            public void end() {
                Vibrator myVibrator = (Vibrator) getApplication().getSystemService(Service.VIBRATOR_SERVICE);
                myVibrator.vibrate(100);
                if (isConnected())
                    detect_start();
                else {
                    Toast.makeText(ObjectDetectActivity.this, "Not connected", Toast.LENGTH_SHORT).show();
                }
            }
        });
        postFragment(fragment, "default");
    }


    private Fragment getFinalFaceFragment(Face face, Fragment next, String nextId) throws IOException {
        FaceFragment faceFragment = new FaceFragment();
        faceFragment.warp(context, face, 2, true);
        faceFragment.setListener(new FragmentFlowListener(next, nextId) {
            @Override
            protected void postFragment(Fragment next, String nextId) {
                ObjectDetectActivity.this.postFragment(next, nextId);
            }

            @Override
            public void end() {
                super.end();
                onComplete();
            }
        });
        return faceFragment;
    }

    private Fragment getFaceFragment(Face face, String name, String tr_name, String sentence, String tr_sentence, Fragment next, String nextId) throws IOException {

        FaceFragment faceFragment = new FaceFragment();
        faceFragment.warp(context, face, 5, false);

        faceFragment.setListener(new FragmentFlowListener(next, nextId) {
            @Override
            protected void postFragment(Fragment next, String nextId) {
                ObjectDetectActivity.this.postFragment(next, nextId);
            }

            @Override
            public void start() {
                super.start();
                speaker.setSpeakerListener(this::end);
                speaker.speakFully(name, tr_name, sentence, tr_sentence);
            }

            @Override
            public void end() {
                super.end();
            }
        });

        return faceFragment;
    }

    public Fragment getDescriptionFragment(String name, String tr_name, Fragment next, String nextId) {
        final DescriptionFragment descriptionFragment = new DescriptionFragment();
        descriptionFragment.setShowListener((views) -> {
            ((ImageView) views[0]).setImageDrawable(context.getDrawable(getObjectDrawableId(name)));
            ((TextView) views[1]).setText(name);
            ((TextView) views[2]).setText(tr_name);
        });

        descriptionFragment.setListener(new FragmentFlowListener(next, nextId) {
            @Override
            public void start() {
                super.start();
                new Thread(() -> {
                    try {
                        Thread.sleep(10000);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    end();
                }).start();
            }

            @Override
            protected void postFragment(Fragment next, String nextId) {
                ObjectDetectActivity.this.postFragment(next, nextId);
            }
        });

        return descriptionFragment;
    }

    private Fragment getExampleFragment(String sentence, String tr_sentence, Fragment next, String nextId) {
        final ExampleFragment fragment = new ExampleFragment();
        fragment.setListener(new FragmentFlowListener(next, nextId) {
            @Override
            protected void postFragment(Fragment next, String nextId) {
                ObjectDetectActivity.this.postFragment(next, nextId);
            }

            @Override
            public void start() {
                super.start();
                speaker.speakExampleSentence(sentence, tr_sentence);
                speaker.setSpeakerListener(this::end);
            }
        });

        fragment.setShowListener(views -> {
            ((TextView) views[0]).setText(sentence);
            ((TextView) views[1]).setText(tr_sentence);
        });
        return fragment;

    }


    @Override
    public void onStop() {
//        sendMessage("PAUSE_DETECT");
        if(isConnected())
            sendMessage("STOP_DETECT");
        speaker.shutdown();
        super.onStop();
    }

    @Override
    protected void onConnect() {
        sendMessage("DETECT_OBJECT");
    }

    @Override
    protected void onDisconnect() {
//        sendMessage("PAUSE_DETECT");
        sendMessage("STOP_DETECT");
    }
}
