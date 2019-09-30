// ------------------------- OpenPose C++ API Tutorial - Example 9 - XXXXXXXXXXXXX -------------------------
// If the user wants to learn to use the OpenPose library, we highly recommend to start with the
// examples in `examples/tutorial_api_cpp/`.
// This example summarizes all the functionality of the OpenPose library:
    // 1. Read folder of images / video / webcam  (`producer` module)
    // 2. Extract and render body keypoint / heatmap / PAF of that image (`pose` module)
    // 3. Extract and render face keypoint / heatmap / PAF of that image (`face` module)
    // 4. Save the results on disk (`filestream` module)
    // 5. Display the rendered pose (`gui` module)
    // Everything in a multi-thread scenario (`thread` module)
    // Points 2 to 5 are included in the `wrapper` module
// In addition to the previous OpenPose modules, we also need to use:
    // 1. `core` module:
        // For the Array<float> class that the `pose` module needs
        // For the Datum struct that the `thread` module sends between the queues
    // 2. `utilities` module: for the error & logging functions, i.e., op::error & op::log respectively
// This file should only be used for the user to take specific examples.

#include <chrono>
#include <iostream>

// Command-line user interface
#include <openpose/flags.hpp>
// OpenPose dependencies
#include <openpose/headers.hpp>

#include <opencv2/opencv.hpp>

#include <boost/asio.hpp>
#include <boost/asio/connect.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/date_time/posix_time/posix_time_io.hpp>
#include <boost/date_time/local_time/local_time.hpp>
#include <boost/date_time/time_zone_base.hpp>
#include <boost/date_time/gregorian/gregorian.hpp>

#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"

#include "base64/base64.h"

namespace date_time = boost::date_time;
namespace json = rapidjson;
namespace local = boost::asio::local;
namespace local_time = boost::local_time;
namespace posix_time = boost::posix_time;

using boost::asio::ip::tcp;

DEFINE_bool(raw_image, false,
            "Whether to stream raw image. if not set, only sends highly "
            "compressed thumbnail");
DEFINE_bool(use_unix_socket, false,
            "Whether to use unix socket. if not set, use TCP");
DEFINE_string(unix_socket, "",
              "Socket address for IPC postprocessing pipeline");
DEFINE_string(tcp_host, "",
              "TCP host for tcp proprocessing pipeline");
DEFINE_string(tcp_port, "",
              "TCP port for tcp preprocessing pipeline");
DEFINE_string(thumbnail_resolution, "240x135",
              "Resolution for JPEG thumbnail");

// If the user needs his own variables, he can inherit the op::Datum struct and add them in there.
// UserDatum can be directly used by the OpenPose wrapper because it inherits from op::Datum, just define
// WrapperT<std::vector<UserDatum>> instead of Wrapper (or equivalently WrapperT<std::vector<UserDatum>>)
struct UserDatum : public op::Datum {
  posix_time::ptime timestamp;

  UserDatum() :
    timestamp{posix_time::microsec_clock::universal_time()}
  {}
};

void parseDatum(bool rawFrame, std::shared_ptr<UserDatum> datum,
                std::string* str) {
  json::StringBuffer s;
  json::Writer<json::StringBuffer> writer(s);
  writer.SetMaxDecimalPlaces(3);

  writer.StartObject();
  std::string timestamp =
    posix_time::to_iso_extended_string(datum->timestamp) + "Z";

  if (rawFrame) {
    writer.Key("rawImage");
    {
      writer.StartObject();

      writer.Key("columns");
      writer.Int(datum->cvInputData.cols);

      writer.Key("rows");
      writer.Int(datum->cvInputData.rows);

      writer.Key("elemSize");
      writer.Int(datum->cvInputData.elemSize());

      writer.Key("elemType");
      writer.Int(datum->cvInputData.type());

      writer.Key("binary");
      auto data = datum->cvInputData.data;
      auto size = datum->cvInputData.dataend - datum->cvInputData.datastart;
      std::string base64_image = base64_encode(data, size);
      writer.String(base64_image.c_str());

      writer.EndObject();
    }
  } else {
    writer.Key("thumbnail");
    {
      writer.StartObject();

      writer.Key("originalColumns");
      writer.Int(datum->cvInputData.cols);

      writer.Key("originalRows");
      writer.Int(datum->cvInputData.rows);

      writer.Key("binary");
      std::string ext(".jpg");
      std::vector<int> comp_params;
      comp_params.push_back(CV_IMWRITE_JPEG_QUALITY);
      comp_params.push_back(50);

      cv::Mat thumbnail;
      op::Point<int> resolution =
        op::flagsToPoint(FLAGS_thumbnail_resolution, "480x270");
      cv::Size size(resolution.x, resolution.y);
      cv::resize(datum->cvInputData, thumbnail, size);

      std::vector<uint8_t> buf;
      cv::imencode(ext, thumbnail, buf, comp_params);

      std::string base64_image = base64_encode(buf.data(), buf.size());
      writer.String(base64_image.c_str());

      writer.EndObject();
    }
  }

  writer.Key("people");
  {
    writer.StartArray();

    for (auto person = 0; person < datum->poseKeypoints.getSize(0); person++) {
      writer.StartObject();

      writer.Key("body");
      writer.StartArray();
      const auto& poseKeypoints = datum->poseKeypoints;
      for (auto bodyPart = 0; bodyPart < poseKeypoints.getSize(1); bodyPart++) {
        writer.Uint(poseKeypoints[{person, bodyPart, 0}]);
        writer.Uint(poseKeypoints[{person, bodyPart, 1}]);
        writer.Double(poseKeypoints[{person, bodyPart, 2}]);
      }
      writer.EndArray();

      if (FLAGS_face) {
        writer.Key("face");
        writer.StartArray();
        const auto& faceKeypoints = datum->faceKeypoints;
        for (auto facePart = 0; facePart < faceKeypoints.getSize(1); facePart++) {
          writer.Uint(faceKeypoints[{person, facePart, 0}]);
          writer.Uint(faceKeypoints[{person, facePart, 1}]);
          writer.Double(faceKeypoints[{person, facePart, 2}]);
        }
        writer.EndArray();
      }

      if (FLAGS_hand) {
        writer.Key("leftHand");
        writer.StartArray();
        const auto& leftHandKeypoints = datum->handKeypoints[0];
        for (auto handPart = 0; handPart < leftHandKeypoints.getSize(1); handPart++) {
          writer.Uint(leftHandKeypoints[{person, handPart, 0}]);
          writer.Uint(leftHandKeypoints[{person, handPart, 1}]);
          writer.Double(leftHandKeypoints[{person, handPart, 2}]);
        }
        writer.EndArray();

        writer.Key("rightHand");
        writer.StartArray();
        const auto& rightHandKeypoints = datum->handKeypoints[1];
        for (auto handPart = 0; handPart < rightHandKeypoints.getSize(1); handPart++) {
          writer.Uint(rightHandKeypoints[{person, handPart, 0}]);
          writer.Uint(rightHandKeypoints[{person, handPart, 1}]);
          writer.Double(rightHandKeypoints[{person, handPart, 2}]);
        }
        writer.EndArray();
      }

      writer.Key("openposeId");
      writer.Uint(person + 1);  // set openposeId start at 1

      writer.EndObject();
    }

    writer.EndArray();
  }

  writer.Key("frameNumber");
  writer.Uint(datum->frameNumber + 1);  // openpose frame number starts at 0
  writer.Key("timestamp");
  writer.String(timestamp.c_str());

  writer.EndObject();

  *str = s.GetString();
}

// The W-classes can be implemented either as a template or as simple classes given
// that the user usually knows which kind of data he will move between the queues,
// in this case we assume a std::shared_ptr of a std::vector of UserDatum


// This worker will just read and return all the jpg files in a directory
using UserDatumVector =
  std::shared_ptr<std::vector<std::shared_ptr<UserDatum>>>;
class WUnixSocketOutput : public op::WorkerConsumer<UserDatumVector> {
 public:
  explicit WUnixSocketOutput(const std::string& address)
    : op::WorkerConsumer<UserDatumVector>(), mAddress(address) {}
  ~WUnixSocketOutput() {
    uint32_t size = 0;
    boost::asio::write(*mSocket, boost::asio::buffer(&size, sizeof(size)));
    mSocket->close();
    delete mSocket;
    delete mEndpoint;
  }

  void initializationOnThread() {
    // The io context is required for all I/O
    boost::asio::io_service ioc;
    mEndpoint = new local::stream_protocol::endpoint(mAddress.c_str());
    mSocket = new local::stream_protocol::socket(ioc);

    // retry 10 times
    bool connected = false;
    for (int i = 0; i < 30; i++) {
      try {
        mSocket->connect(*mEndpoint);
        connected = true;
        break;
      } catch (const std::exception& e) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
      }
    }

    if (!connected) {
      op::error("failed to establish connection to unix socket", __LINE__, __FUNCTION__, __FILE__);
    }
  }

  void workConsumer(const std::shared_ptr<std::vector<std::shared_ptr<UserDatum>>>& datumsPtr) {
    try {
      if (datumsPtr != nullptr && !datumsPtr->empty()) {
        const auto profilerKey = op::Profiler::timerInit(__LINE__, __FUNCTION__, __FILE__);

        // Parse output into json
        std::string parsedJsonStr;
        parseDatum(FLAGS_raw_image, datumsPtr->at(0), &parsedJsonStr);
        uint32_t size = parsedJsonStr.size();
        boost::asio::write(*this->mSocket, boost::asio::buffer(&size, sizeof(size)));
        boost::asio::write(*this->mSocket, boost::asio::buffer(parsedJsonStr.c_str(), parsedJsonStr.size()));

        op::Profiler::timerEnd(profilerKey);
        op::Profiler::printAveragedTimeMsOnIterationX(profilerKey, __LINE__, __FUNCTION__, __FILE__);
      }
    } catch (const std::exception& e) {
      this->stop();
      op::error(e.what(), __LINE__, __FUNCTION__, __FILE__);
    }
  }

 private:
  std::string mAddress;
  local::stream_protocol::endpoint* mEndpoint;
  local::stream_protocol::socket* mSocket;
};

class WTCPSocketOutput : public op::WorkerConsumer<UserDatumVector> {
 public:
  explicit WTCPSocketOutput(const std::string& host, const std::string& port)
    : op::WorkerConsumer<UserDatumVector>(), mHost(host), mPort(port) {}
  ~WTCPSocketOutput() {
    uint32_t size = 0;
    boost::asio::write(*this->mSocket, boost::asio::buffer(&size, sizeof(size)));
    mSocket->close();
    delete mSocket;
  }

  void initializationOnThread() {
    // The io context is required for all I/O
    boost::asio::io_service ioc;

    mSocket = new tcp::socket(ioc);
    mResolver = new tcp::resolver(ioc);

    // retry 10 times
    bool connected = false;
    for (int i = 0; i < 30; i++) {
      try {
        boost::asio::connect(*mSocket, mResolver->resolve({mHost, mPort}));
        connected = true;
        break;
      } catch (const std::exception& e) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
      }
    }

    if (!connected) {
      op::error("failed to establish connection to tcp socket", __LINE__, __FUNCTION__, __FILE__);
    }
  }

  void workConsumer(const std::shared_ptr<std::vector<std::shared_ptr<UserDatum>>>& datumsPtr) {
    try {
      if (datumsPtr != nullptr && !datumsPtr->empty()) {
        const auto profilerKey = op::Profiler::timerInit(__LINE__, __FUNCTION__, __FILE__);

        // Parse output into json
        std::string parsedJsonStr;
        parseDatum(FLAGS_raw_image, datumsPtr->at(0), &parsedJsonStr);
        uint32_t size = parsedJsonStr.size();
        boost::asio::write(*mSocket, boost::asio::buffer(&size, sizeof(size)));
        boost::asio::write(*mSocket, boost::asio::buffer(parsedJsonStr.c_str(), parsedJsonStr.size()));

        op::Profiler::timerEnd(profilerKey);
        op::Profiler::printAveragedTimeMsOnIterationX(profilerKey, __LINE__, __FUNCTION__, __FILE__);
      }
    } catch (const std::exception& e) {
      this->stop();
      op::error(e.what(), __LINE__, __FUNCTION__, __FILE__);
    }
  }

 private:
  std::string mHost;
  std::string mPort;
  tcp::socket* mSocket;
  tcp::resolver* mResolver;
};

int tutorialApiCpp8() {
  try {
    op::log("Starting OpenPose demo...", op::Priority::High);
    const auto timerBegin = std::chrono::high_resolution_clock::now();

    // logging_level
    op::check(0 <= FLAGS_logging_level && FLAGS_logging_level <= 255, "Wrong logging_level value.",
        __LINE__, __FUNCTION__, __FILE__);
    op::ConfigureLog::setPriorityThreshold((op::Priority)FLAGS_logging_level);
    op::Profiler::setDefaultX(FLAGS_profile_speed);
    // // For debugging
    // // Print all logging messages
    // op::ConfigureLog::setPriorityThreshold(op::Priority::None);
    // // Print out speed values faster
    // op::Profiler::setDefaultX(100);

    // Applying user defined configuration - GFlags to program variables
    // cameraSize
    const auto cameraSize = op::flagsToPoint(FLAGS_camera_resolution, "-1x-1");
    // outputSize
    const auto outputSize = op::flagsToPoint(FLAGS_output_resolution, "-1x-1");
    // netInputSize
    const auto netInputSize = op::flagsToPoint(FLAGS_net_resolution, "-1x368");
    // faceNetInputSize
    const auto faceNetInputSize = op::flagsToPoint(
        FLAGS_face_net_resolution, "368x368 (multiples of 16)");
    // handNetInputSize
    const auto handNetInputSize = op::flagsToPoint(
        FLAGS_hand_net_resolution, "368x368 (multiples of 16)");
    // producerType
    op::ProducerType producerType;
    std::string producerString;
    std::tie(producerType, producerString) = op::flagsToProducer(
        FLAGS_image_dir, FLAGS_video, FLAGS_ip_camera, FLAGS_camera,
        FLAGS_flir_camera, FLAGS_flir_camera_index);
    // poseMode
    const auto poseMode = op::flagsToPoseMode(FLAGS_body);

    // poseModel
    const auto poseModel = op::flagsToPoseModel(FLAGS_model_pose);
    // JSON saving
    if (!FLAGS_write_keypoint.empty())
      op::log(
          "Flag `write_keypoint` is deprecated and will eventually be removed."
          " Please, use `write_json` instead.", op::Priority::Max);
    // keypointScale
    const auto keypointScaleMode = op::flagsToScaleMode(FLAGS_keypoint_scale);
    // heatmaps to add
    const auto heatMapTypes =
      op::flagsToHeatMaps(FLAGS_heatmaps_add_parts, FLAGS_heatmaps_add_bkg,
                          FLAGS_heatmaps_add_PAFs);
    const auto heatMapScaleMode = op::flagsToHeatMapScaleMode(FLAGS_heatmaps_scale);
    // >1 camera view?
    const auto multipleView = (FLAGS_3d || FLAGS_3d_views > 1 || FLAGS_flir_camera);

    // Face and hand detectors
    const auto faceDetector = op::flagsToDetector(FLAGS_face_detector);
    const auto handDetector = op::flagsToDetector(FLAGS_hand_detector);

    // Enabling Google Logging
    const bool enableGoogleLogging = true;

    // OpenPose wrapper
    op::log("Configuring OpenPose...", op::Priority::High);
    op::WrapperT<UserDatum> opWrapperT;

    std::shared_ptr<op::WorkerConsumer<UserDatumVector>> wUserOutput;
    // Initializing the user custom classes
    // GUI (Display)
    if (FLAGS_use_unix_socket) {
      wUserOutput = std::make_shared<WUnixSocketOutput>(FLAGS_unix_socket);
    } else {
      wUserOutput = std::make_shared<WTCPSocketOutput>(FLAGS_tcp_host, FLAGS_tcp_port);
    }

    // Add custom processing
    const auto workerOutputOnNewThread = true;
    opWrapperT.setWorker(op::WorkerType::Output, wUserOutput, workerOutputOnNewThread);

    // Pose configuration (use WrapperStructPose{} for default and recommended configuration)
    const op::WrapperStructPose wrapperStructPose{
      poseMode, netInputSize, outputSize, keypointScaleMode, FLAGS_num_gpu, FLAGS_num_gpu_start,
        FLAGS_scale_number, static_cast<float>(FLAGS_scale_gap), op::flagsToRenderMode(FLAGS_render_pose, multipleView),
        poseModel, !FLAGS_disable_blending, static_cast<float>(FLAGS_alpha_pose), static_cast<float>(FLAGS_alpha_heatmap),
        FLAGS_part_to_show, FLAGS_model_folder, heatMapTypes, heatMapScaleMode, FLAGS_part_candidates,
        static_cast<float>(FLAGS_render_threshold), FLAGS_number_people_max, FLAGS_maximize_positives, FLAGS_fps_max,
        FLAGS_prototxt_path, FLAGS_caffemodel_path, static_cast<float>(FLAGS_upsampling_ratio), enableGoogleLogging};
    opWrapperT.configure(wrapperStructPose);

    // Face configuration (use op::WrapperStructFace{} to disable it)
    const op::WrapperStructFace wrapperStructFace{
      FLAGS_face, faceDetector, faceNetInputSize,
        op::flagsToRenderMode(FLAGS_face_render, multipleView, FLAGS_render_pose),
        static_cast<float>(FLAGS_face_alpha_pose), static_cast<float>(FLAGS_face_alpha_heatmap), static_cast<float>(FLAGS_face_render_threshold)};
    opWrapperT.configure(wrapperStructFace);

    // Hand configuration (use op::WrapperStructHand{} to disable it)
    const op::WrapperStructHand wrapperStructHand{
      FLAGS_hand, handDetector, handNetInputSize, FLAGS_hand_scale_number, static_cast<float>(FLAGS_hand_scale_range),
        op::flagsToRenderMode(FLAGS_hand_render, multipleView, FLAGS_render_pose), static_cast<float>(FLAGS_hand_alpha_pose),
        static_cast<float>(FLAGS_hand_alpha_heatmap), static_cast<float>(FLAGS_hand_render_threshold)};
    opWrapperT.configure(wrapperStructHand);

    // Extra functionality configuration (use op::WrapperStructExtra{} to disable it)
    const op::WrapperStructExtra wrapperStructExtra{
      FLAGS_3d, FLAGS_3d_min_views, FLAGS_identification, FLAGS_tracking, FLAGS_ik_threads};
    opWrapperT.configure(wrapperStructExtra);

    // Producer (use default to disable any input)
    const op::WrapperStructInput wrapperStructInput{
      producerType, producerString, FLAGS_frame_first, FLAGS_frame_step, FLAGS_frame_last,
        FLAGS_process_real_time, FLAGS_frame_flip, FLAGS_frame_rotate, FLAGS_frames_repeat,
        cameraSize, FLAGS_camera_parameter_path, FLAGS_frame_undistort, FLAGS_3d_views};
    opWrapperT.configure(wrapperStructInput);

    // Output (comment or use default argument to disable any output)
    const op::WrapperStructOutput wrapperStructOutput{
      FLAGS_cli_verbose, FLAGS_write_keypoint, op::stringToDataFormat(FLAGS_write_keypoint_format),
        FLAGS_write_json, FLAGS_write_coco_json, FLAGS_write_coco_json_variants, FLAGS_write_coco_json_variant,
        FLAGS_write_images, FLAGS_write_images_format, FLAGS_write_video, FLAGS_write_video_fps,
        FLAGS_write_video_with_audio, FLAGS_write_heatmaps, FLAGS_write_heatmaps_format, FLAGS_write_video_3d,
        FLAGS_write_video_adam, FLAGS_write_bvh, FLAGS_udp_host, FLAGS_udp_port};
    opWrapperT.configure(wrapperStructOutput);

    // No GUI. Equivalent to: opWrapper.configure(op::WrapperStructGui{});
    // Set to single-thread (for sequential processing and/or debugging and/or reducing latency)
    if (FLAGS_disable_multi_thread)
      opWrapperT.disableMultiThreading();

    // Start, run, and stop processing - exec() blocks this thread until OpenPose wrapper has finished
    op::log("Starting thread(s)...", op::Priority::High);
    opWrapperT.exec();

    // Measuring total time
    const auto now = std::chrono::high_resolution_clock::now();
    const auto totalTimeSec = static_cast<double>(std::chrono::duration_cast<std::chrono::nanoseconds>(now-timerBegin).count()
      * 1e-9);
    const auto message = "OpenPose demo successfully finished. Total time: "
      + std::to_string(totalTimeSec) + " seconds.";
    op::log(message, op::Priority::High);

    // Return successful message
    return 0;
  }
  catch (const std::exception& e) {
    return -1;
  }
}

int main(int argc, char *argv[]) {
  // Parsing command line flags
  gflags::ParseCommandLineFlags(&argc, &argv, true);

  // Running tutorialApiCpp8
  return tutorialApiCpp8();
}
