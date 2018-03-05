package com.grp5.mdp.cz3004;

import android.annotation.SuppressLint;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.IntentFilter;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.support.v4.app.Fragment;
import android.support.design.widget.NavigationView;
import android.support.v4.app.FragmentActivity;
import android.support.v4.app.FragmentManager;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.KeyEvent;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.inputmethod.EditorInfo;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import java.math.BigInteger;

public class MainActivity extends AppCompatActivity
        implements NavigationView.OnNavigationItemSelectedListener,
        BluetoothFragment.OnFragmentInteractionListener,
        SendTextFragment.OnFragmentInteractionListener,
        ArenaFragment.OnMapUpdateListener,
        MiscellaneousFragment.OnFragmentInteractionListener{

    private BluetoothAdapter BTAdapter;
    private Fragment fragment;

    BluetoothChatService mChatService;
    String arduinoAddr;

    /**
     * String buffer for outgoing messages
     */
    private StringBuffer mOutStringBuffer;

    public static int REQUEST_BLUETOOTH = 1;

    /**
     * Name of the connected device
     */
    private String mConnectedDeviceName = null;

    @SuppressLint("HandlerLeak")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        BTAdapter = BluetoothAdapter.getDefaultAdapter();

        // Phone does not support Bluetooth so let the user know and exit.
        if (BTAdapter == null) {
            new AlertDialog.Builder(this)
                    .setTitle("Not compatible")
                    .setMessage("Your phone does not support Bluetooth")
                    .setPositiveButton("Exit", new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog, int which) {
                            System.exit(0);
                        }
                    })
                    .setIcon(android.R.drawable.ic_dialog_alert)
                    .show();
        }

        if (!BTAdapter.isEnabled()) {
            Intent enableBT = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivityForResult(enableBT, REQUEST_BLUETOOTH);
        }

        // Initialize the BluetoothChatService to perform bluetooth connections
        mChatService = new BluetoothChatService(MainActivity.this, readHandler);

        // Initialize the buffer for outgoing messages
        mOutStringBuffer = new StringBuffer("");

        // Check that the activity is using the layout version with
        // the fragment_container FrameLayout
        if (findViewById(R.id.fragment_container) != null) {

            // However, if we're being restored from a previous state,
            // then we don't need to do anything and should return or else
            // we could end up with overlapping fragments.
            if (savedInstanceState != null) {
                return;
            }

            // Create a new Fragment to be placed in the activity layout
            BluetoothFragment btFragment = BluetoothFragment.newInstance(BTAdapter, mChatService);

            // In case this activity was started with special instructions from an
            // Intent, pass the Intent's extras to the fragment as arguments
            btFragment.setArguments(getIntent().getExtras());

            // Add the fragment to the 'fragment_container' FrameLayout
            getSupportFragmentManager().beginTransaction()
                    .add(R.id.fragment_container, btFragment).commit();
        }

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(
                this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        drawer.addDrawerListener(toggle);
        toggle.syncState();

        NavigationView navigationView = (NavigationView) findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);

    }

    @Override
    public void onBackPressed() {
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        if (drawer.isDrawerOpen(GravityCompat.START)) {
            drawer.closeDrawer(GravityCompat.START);
        } else {
            super.onBackPressed();
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    @SuppressWarnings("StatementWithEmptyBody")
    @Override
    public boolean onNavigationItemSelected(MenuItem item) {
        String tagText;
        Fragment fragment;
        FragmentManager fm = getSupportFragmentManager();

        // Handle navigation view item clicks here.
        int id = item.getItemId();

        if (id == R.id.nav_bluetooth) {
            tagText = "BluetoothFragment";
            fragment = fm.findFragmentByTag(tagText);
            if (fragment == null) {
                fragment = BluetoothFragment.newInstance(BTAdapter, mChatService);
            }
        } else if (id == R.id.nav_sendText) {
            tagText = "SendTextFragment";
            fragment = fm.findFragmentByTag(tagText);
            if (fragment == null) {
                fragment = SendTextFragment.newInstance(BTAdapter, mChatService);
            }
        } else if (id == R.id.nav_arena) {
            tagText = "ArenaFragment";
            fragment = fm.findFragmentByTag(tagText);
            if (fragment == null) {
                fragment = ArenaFragment.newInstance(BTAdapter, mChatService);
            }
        }  else if (id == R.id.nav_misc) {
            tagText = "MiscFragment";
            fragment = fm.findFragmentByTag(tagText);
            if (fragment == null) {
                fragment = MiscellaneousFragment.newInstance(BTAdapter, mChatService);
            }
        } else {
            fragment=null;
            tagText=null;
        }

        fm.beginTransaction().replace(R.id.fragment_container, fragment, tagText)
                .addToBackStack(tagText)
                .commit();

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }

    @Override
    public void onFragmentInteraction(String deviceAddress) {
        arduinoAddr = deviceAddress;
    }

    /**
     * The Handler that gets information back from the BluetoothChatService
     */
    @SuppressLint("HandlerLeak")
    private final Handler readHandler = new Handler() {
        @Override
        public void handleMessage(Message msg) {
            TextView bluetooth = (TextView) findViewById(R.id.statusText);
            TextView arena = (TextView) findViewById(R.id.bluetoothStatus);
            //TODO: put statustext into arena fragment
            switch (msg.what) {
                case Constants.MESSAGE_STATE_CHANGE:
                    switch (msg.arg1) {
                        case BluetoothChatService.STATE_CONNECTED:
                            if(bluetooth != null){
                                bluetooth.setText(getString(R.string.title_connected_to, mConnectedDeviceName));
                            }
                            else if (arena != null){
                                arena.setText(getString(R.string.title_connected_to, mConnectedDeviceName));
                            }
                            break;
                        case BluetoothChatService.STATE_CONNECTING:
                            if(bluetooth != null){
                                bluetooth.setText(R.string.title_connecting);
                            }
                            else if (arena != null){
                                arena.setText(R.string.title_connecting);
                            }
                            break;
                        case BluetoothChatService.STATE_NONE:
                            if(bluetooth != null){
                                bluetooth.setText(R.string.bluetooth_disconnected);
                            }
                            else if (arena != null){
                                arena.setText(R.string.bluetooth_disconnected);
                            }
                            break;
                        case BluetoothChatService.STATE_LOST:
                            if(bluetooth != null){
                                bluetooth.setText(R.string.bluetooth_disconnected);
                            }
                            else if (arena != null){
                                arena.setText(R.string.bluetooth_disconnected);
                            }
                            break;
                    }
                    break;
                case Constants.MESSAGE_READ:
                    byte[] readBuf = (byte[]) msg.obj;
                    // construct a string from the valid bytes in the buffer
                    String readMessage = new String(readBuf, 0, msg.arg1);
                    TextView rf = (TextView) findViewById(R.id.readField);
                    if(rf != null){
                        rf.setText(readMessage);
                    }
                    if(readMessage.startsWith("MDF") || readMessage.startsWith("DIR")){
                        onMapUpdateReceived(readMessage);
                    }
                    break;
                case Constants.MESSAGE_DEVICE_NAME:
                    // save the connected device's name
                    mConnectedDeviceName = msg.getData().getString(Constants.DEVICE_NAME);
                    Toast.makeText(MainActivity.this, "Connected to "
                            + mConnectedDeviceName, Toast.LENGTH_SHORT).show();
                    break;
                case Constants.MESSAGE_TOAST:
                    Toast.makeText(MainActivity.this, msg.getData().getString(Constants.TOAST),
                            Toast.LENGTH_SHORT).show();
                    break;
            }
        }
    };

    String hexToBinary(String hex) {
        return new BigInteger("1" + hex,16).toString(2).substring(1);
    }

    /**
     * Sends a message.
     *
     * @param message A string of text to send.
     */
    protected void sendMessage(String message) {
        EditText mOutEditText = (EditText) findViewById(R.id.writeField);

        // Check that we're actually connected before trying anything
        if (mChatService.getState() != BluetoothChatService.STATE_CONNECTED) {
            Toast.makeText(MainActivity.this, R.string.not_connected, Toast.LENGTH_SHORT).show();
            return;
        }

        // Check that there's actually something to send
        if (message.length() > 0) {
            // Get the message bytes and tell the BluetoothChatService to write
            byte[] send = message.getBytes();
            mChatService.write(send);

            if(mOutEditText != null){
                // Reset out string buffer to zero and clear the edit text field
                mOutStringBuffer.setLength(0);
                mOutEditText.setText(mOutStringBuffer);

                // Initialize the compose field with a listener for the return key
                mOutEditText.setOnEditorActionListener(mWriteListener);
            }
        }
    }

    /**
     * The action listener for the EditText widget, to listen for the return key
     */
    private TextView.OnEditorActionListener mWriteListener
            = new TextView.OnEditorActionListener() {
        public boolean onEditorAction(TextView view, int actionId, KeyEvent event) {
            // If the action is a key-up event on the return key, send the message
            if (actionId == EditorInfo.IME_NULL && event.getAction() == KeyEvent.ACTION_UP) {
                String message = view.getText().toString();
                sendMessage(message);
            }
            return true;
        }
    };

    @Override
    public void onFragmentInteraction(Uri uri) {

    }

    public void onMapUpdateReceived(String message){
        //pass the strings to arena fragment to be parsed
        ArenaFragment arenaFrag = (ArenaFragment) getSupportFragmentManager().findFragmentByTag("ArenaFragment");
        Log.d("MDF_OR_DIR", message);
        if(arenaFrag != null){
            if(message.startsWith("MDF")){
                String mdfStr = message.substring(3);
                String exploredHexStr = mdfStr.split("L")[0];
                String obstacleHexStr = mdfStr.split("L")[1];
                String exploredBin = hexToBinary(exploredHexStr);
                String obstacleBin = hexToBinary(obstacleHexStr);
                arenaFrag.updateMap(exploredBin.substring(2, 302), obstacleBin);
            } else if (message.startsWith("DIR")) {
                String dirStr = message.substring(3);
                String dirRow = dirStr.split("L")[0];
                String dirCol = dirStr.split("L")[1];
                String dirDir = dirStr.split("L")[2];
                String dirMoveOrStop = dirStr.split("L")[3];
                arenaFrag.updateRobot(dirRow, dirCol, dirDir, dirMoveOrStop);
            }
        }
    }
}
